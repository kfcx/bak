// 旧版代码。但是比较完善，没有外存

import { Application, Router } from "https://deno.land/x/oak/mod.ts";
import { Session, CookieStore } from "https://deno.land/x/oak_sessions/mod.ts";
import { OAuth2Client } from "jsr:@cmd-johnson/oauth2-client@^2.0.0";


// 1 已缓存   // 解决重复深度查询问题
// 2 未缓存
// 3 1、mem2 => 2
// 4 1、mem1、mem2 => 2
// 5 2、mem2
// 缓存同步问题，需要减少内缓存查询，已有内缓存但是查询密码错误信息会覆盖外缓存
// 解决：外缓存记录正确pwd，每次都校验pwd
// 引申出三种外缓存策略
// 1. 外缓存不记录错误信息，记录内缓存后不再改变。缺点：占内存
// 2. 外缓存每次记录错误信息，正确密码再请求内缓存。缺点：需要更多次内查询
// 3. 根据文件大小决定策略1或2
// pwd正确 && 未缓存 => 深入搜索 ( || memData.pwd === pwd)
// 未缓存key标记  // 小坑：更新标记后会覆盖已缓存标记

type AppState = {
  session: Session;
};
const app = new Application<AppState>();
const router = new Router<AppState>();
const store = new CookieStore("session_data")

const memCache = new Map();
const kv = await Deno.openKv();
const cache = await caches.open("pastes1"); // 使用单独的 caches 空间

const PASTE_STORE = 'P'; // PASTE_STORE KV 命名空间
const MAXSIZE = 5 * 1024 * 1024;  // 5MB
const kvMAXSIZE = 1048576;  // 1MB
const VALID_CHARS_REGEX = /^[a-zA-Z0-9-\.]+$/;
const mimeTypeRegex = /^[-\w.+]+\/[-\w.+]+(?:;\s*[-\w]+=[-\w]+)*$/i;
const keywords = new Set<number>(["example", "p", "d", "s", "n"]);


// https://github.com/cmd-johnson/deno-oauth2-client
const oauth2Client = new OAuth2Client({
  clientId: Deno.env.get("CLIENT_ID")!,
  clientSecret: Deno.env.get("CLIENT_SECRET")!,
  authorizationEndpointUri: "https://connect.linux.do/oauth2/authorize",
  tokenUri: "https://connect.linux.do/oauth2/token",
  redirectUri: "https://qbin.me/oauth2/callback",
  defaults: { scope: "user:profile",},
});


interface Metadata {
  time: number;
  ip: string;
  content: string | ArrayBuffer;  // 支持字符串或二进制内容 Uint8Array
  type: string;
  len: number;
  pwd?: string;
}

const HEADERS = {
  HTML: {
    "X-Content-Type-Options": "nosniff",    // 禁止嗅探MIME类型
    "X-XSS-Protection": "1; mode=block",    // 启用XSS过滤器
    "X-Frame-Options": "DENY",              // 禁止页面在frame中展示
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",  // HSTS强制使用HTTPS
    "Referrer-Policy": "strict-origin-when-cross-origin",      // 引用策略
  },
  JSON: { "Content-Type": "application/json" },
  CORS: {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
  }
};


// 优化错误处理
class PasteError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'PasteError';
  }
}

function renderHtml(metadata){
    let initialData = null;
    if (metadata.type.startsWith('text/')) {
        let content = metadata.content;
        if (typeof content !== 'string'){
            content = new TextDecoder('utf-8').decode(content);
        }
        initialData = {
            type: metadata.type,
            content: content,
            // time: metadata.time,
            len: metadata.len
        };
    } else if (metadata.type.startsWith('image/')) {
        const uint8Array = new Uint8Array(metadata.content as ArrayBuffer);
        const base64Content = btoa(
            uint8Array.reduce((data, byte) => data + String.fromCharCode(byte), '')
        );
        initialData = {
            type: metadata.type,
            content: `data:${metadata.type};base64,${base64Content}`,
            // time: metadata.time,
            len: metadata.len
        };
    } else {
        // 其他类型文件只传递元数据
        initialData = {
            type: metadata.type,
            // time: metadata.time,
            len: metadata.len
        };
    }

    const html = `
  <!DOCTYPE html>
  <html>
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
      <link rel="icon" type="image/svg+xml" href="https://ik.imagekit.io/naihe/logo/qbin.svg">
      <title>QBin</title>
      <style>
          body{margin:0;padding:0;min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;display:flex;flex-direction:column}.header{padding:12px 16px;display:flex;justify-content:flex-end;gap:8px;background:#fff;border-bottom:1px solid #f0f0f0}.button{padding:6px 12px;border-radius:4px;border:1px solid #e0e0e0;background:#fff;color:#666;cursor:pointer;font-size:13px;transition:all .2s;min-width:50px;text-align:center}.button:disabled{opacity:.6;cursor:not-allowed;pointer-events:none}.button.processing{position:relative;color:transparent!important}.button.processing::after{content:'';position:absolute;left:50%;top:50%;width:16px;height:16px;margin:-8px 0 0 -8px;border:2px solid rgba(0,0,0,.1);border-top-color:#1890ff;border-radius:50%;animation:button-loading-spinner .6s linear infinite}.button:hover{background:#f5f5f5;color:#1890ff;border-color:#1890ff}.button.primary{background:#1890ff;color:#fff;border-color:#1890ff}.button.primary:hover{background:#40a9ff;border-color:#40a9ff}.button.danger{color:#ff4d4f;border-color:#ff4d4f}.button.danger:hover{background:#fff1f0}.button-group{display:flex;gap:4px}.divider{width:1px;background:#e0e0e0;margin:0 8px}.content{flex:1;padding:20px;box-sizing:border-box}#viewer{width:100%;height:calc(100vh - 100px);border:none;resize:none;font-size:16px;line-height:1.6;padding:15px;box-sizing:border-box;background:#fff}#imageViewer{max-width:100%;max-height:calc(100vh - 100px);margin:0 auto;display:block}.file-info{text-align:center;padding:20px;font-size:16px;color:#666}.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,.7);color:#fff;padding:10px 20px;border-radius:4px;font-size:14px;z-index:1000;animation:fadeIn .3s ease}@keyframes fadeIn{from{opacity:0;transform:translate(-50%,20px)}to{opacity:1;transform:translate(-50%,0)}}@keyframes button-loading-spinner{from{transform:rotate(0)}to{transform:rotate(360deg)}}@media (max-width:768px){.header{padding:15px}.button{padding:6px 12px;font-size:13px}.content{padding:15px}}@supports (-webkit-touch-callout:none){#viewer{touch-action:manipulation}.button{touch-action:manipulation}}
      </style>
  </head>
  <body>
      <div class="header" id="buttonBar"></div>
      <div class="content" id="contentArea"></div>
      <script id="initial-data" type="application/json">
        ${encodeURIComponent(JSON.stringify(initialData))}
      </script>
      <script>
          const _0x461e4e=_0x486f;function _0x3366(){const _0x2d12ab=['innerHTML','onclick','clearLocalCache','/d/','clearContent','image/','handleImageContent','textContent','784938nsyLju','getTime','4908dNwmvO','imageViewer','文件类型:\x20','now','Content-Type','img','链接已复制到剪贴板','.toast','showToast','handleRaw','type','copyLink','button-group','disabled','file-info','2704170kMYWXS','pathname','div','copyContent','大小:\x20','handleFork','replace','join','className','startsWith','clipboard','handleTextContent','error','button','message','set','lastClickTime','textarea','__INITIAL_DATA__','createElement','buttonBar','复制链接失败:','divider','handleNew','New','name','json','viewer','stringify','Raw','parse','99kxngXb','text/','value','contentArea','apply','debounceTimeouts','2937624oOtdeg','writeText','href','/p/','getElementById','get','readOnly','clickTimeout','content','initial-data','Fork','location','removeItem','has','5555110Shhavm','init','Del','len','addButton','handleCopy','blob','text','headers','isProcessing','handleDelete','20xmmNMn','danger','appendChild','799674lLSrPP','src','复制失败，请手动复制','secondary','pasteBoard_cache','9TAJxmw','classList','querySelector','setupButtons','handleDownload','body','Down','CACHE_KEY','398394uHFpHe','add','debounce'];_0x3366=function(){return _0x2d12ab;};return _0x3366();}function _0x486f(_0x126dc6,_0xd34d23){const _0x336668=_0x3366();return _0x486f=function(_0x486f99,_0x585049){_0x486f99=_0x486f99-0xe9;let _0x268631=_0x336668[_0x486f99];return _0x268631;},_0x486f(_0x126dc6,_0xd34d23);}(function(_0x3b2b7c,_0x3e1e23){const _0x199c81=_0x486f,_0x4be536=_0x3b2b7c();while(!![]){try{const _0x12b03e=-parseInt(_0x199c81(0x12b))/0x1+-parseInt(_0x199c81(0x136))/0x2+parseInt(_0x199c81(0xfc))/0x3*(-parseInt(_0x199c81(0x138))/0x4)+-parseInt(_0x199c81(0x11b))/0x5*(-parseInt(_0x199c81(0x11e))/0x6)+parseInt(_0x199c81(0x147))/0x7+-parseInt(_0x199c81(0x102))/0x8+parseInt(_0x199c81(0x123))/0x9*(parseInt(_0x199c81(0x110))/0xa);if(_0x12b03e===_0x3e1e23)break;else _0x4be536['push'](_0x4be536['shift']());}catch(_0x3aba0a){_0x4be536['push'](_0x4be536['shift']());}}}(_0x3366,0x4379c),window[_0x461e4e(0xef)]=JSON[_0x461e4e(0xfb)](decodeURIComponent(document[_0x461e4e(0x106)](_0x461e4e(0x10b))[_0x461e4e(0x135)])));class Viewer{constructor(){const _0x2e1943=_0x461e4e;this['lastClickTime']=0x0,this[_0x2e1943(0x109)]=null,this[_0x2e1943(0x12a)]=_0x2e1943(0x122),this['buttonBar']=document[_0x2e1943(0x106)](_0x2e1943(0xf1)),this['contentArea']=document['getElementById'](_0x2e1943(0xff)),this[_0x2e1943(0x119)]=![],this['debounceTimeouts']=new Map(),this['init']();}async[_0x461e4e(0x111)](){const _0x44ecfa=_0x461e4e;if(window[_0x44ecfa(0xef)]){const _0x517471=window[_0x44ecfa(0xef)];this[_0x44ecfa(0x132)](),this['setupButtons'](_0x517471[_0x44ecfa(0x142)]);if(_0x517471[_0x44ecfa(0x142)][_0x44ecfa(0x150)](_0x44ecfa(0xfd))){const _0x2b9b57=document['createElement'](_0x44ecfa(0xee));_0x2b9b57['id']=_0x44ecfa(0xf8),_0x2b9b57[_0x44ecfa(0xfe)]=_0x517471[_0x44ecfa(0x10a)],_0x2b9b57['readOnly']=!![],this['contentArea'][_0x44ecfa(0x11d)](_0x2b9b57);}else{if(_0x517471[_0x44ecfa(0x142)][_0x44ecfa(0x150)](_0x44ecfa(0x133))){const _0x3905d7=document[_0x44ecfa(0xf0)](_0x44ecfa(0x13d));_0x3905d7['id']=_0x44ecfa(0x139),_0x3905d7['src']=_0x517471[_0x44ecfa(0x10a)],this['contentArea'][_0x44ecfa(0x11d)](_0x3905d7);}else{const _0x476d46=document[_0x44ecfa(0xf0)]('div');_0x476d46[_0x44ecfa(0x14f)]=_0x44ecfa(0x146),_0x476d46[_0x44ecfa(0x135)]=[_0x44ecfa(0x13a),_0x517471[_0x44ecfa(0x142)],'\x5ct',_0x44ecfa(0x14b),Math['ceil'](_0x517471[_0x44ecfa(0x113)]/0x400),'KB'][_0x44ecfa(0x14e)](''),this['contentArea'][_0x44ecfa(0x11d)](_0x476d46);}}}else{const _0x16604b=window[_0x44ecfa(0x10d)]['pathname'];_0x16604b[_0x44ecfa(0x150)](_0x44ecfa(0x105))&&await this['loadContent'](_0x16604b['replace'](_0x44ecfa(0x105),'/'));}}async['loadContent'](_0x176432){const _0x2e2abe=_0x461e4e;try{const _0x1fdced=await fetch(_0x176432),_0x56703a=_0x1fdced[_0x2e2abe(0x118)][_0x2e2abe(0x107)](_0x2e2abe(0x13c));this[_0x2e2abe(0x132)](),this[_0x2e2abe(0x126)](_0x56703a);if(_0x56703a[_0x2e2abe(0x150)](_0x2e2abe(0xfd)))await this[_0x2e2abe(0x152)](_0x1fdced);else _0x56703a[_0x2e2abe(0x150)]('image/')?await this[_0x2e2abe(0x134)](_0x1fdced):await this['handleFileContent'](_0x1fdced,_0x56703a);}catch(_0x13597b){console[_0x2e2abe(0xe9)]('加载内容失败:',_0x13597b);}}['clearContent'](){const _0x2fcad1=_0x461e4e;this[_0x2fcad1(0xf1)][_0x2fcad1(0x12e)]='',this['contentArea']['innerHTML']='';}[_0x461e4e(0x12d)](_0x5740ec,_0x2f2684=0x5){const _0x19ecf4=_0x461e4e,_0x1a4165=_0x5740ec[_0x19ecf4(0xf6)];return async(..._0x1aefc2)=>{const _0x460a0a=_0x19ecf4;if(this[_0x460a0a(0x119)])return;return this['debounceTimeouts'][_0x460a0a(0x10f)](_0x1a4165)&&clearTimeout(this[_0x460a0a(0x101)]['get'](_0x1a4165)),new Promise(_0x9b6572=>{const _0x2af535=_0x460a0a,_0x4588ba=setTimeout(async()=>{const _0x3b6e53=_0x486f;this[_0x3b6e53(0x119)]=!![];try{await _0x5740ec[_0x3b6e53(0x100)](this,_0x1aefc2),_0x9b6572();}catch(_0x5855ce){console[_0x3b6e53(0xe9)](_0x5855ce);}finally{this[_0x3b6e53(0x119)]=![],this['debounceTimeouts']['delete'](_0x1a4165);}},_0x2f2684);this[_0x2af535(0x101)][_0x2af535(0xec)](_0x1a4165,_0x4588ba);});};}['setupButtons'](_0x245b88){const _0x1bc2a2=_0x461e4e,_0x4a3fbc=document[_0x1bc2a2(0xf0)](_0x1bc2a2(0x149)),_0x51a46c=document['createElement'](_0x1bc2a2(0x149));_0x4a3fbc[_0x1bc2a2(0x14f)]=_0x1bc2a2(0x144),_0x51a46c[_0x1bc2a2(0x14f)]=_0x1bc2a2(0x144);const _0x4f0164=this['addButton']('Copy',()=>this[_0x1bc2a2(0x115)]());_0x4a3fbc[_0x1bc2a2(0x11d)](_0x4f0164);const _0x35602d=this['debounce'](()=>this[_0x1bc2a2(0x14c)]()),_0x12e6fe=this[_0x1bc2a2(0x12d)](()=>this[_0x1bc2a2(0x141)]()),_0x3aaa4a=this[_0x1bc2a2(0x12d)](()=>this[_0x1bc2a2(0xf4)]()),_0x321f69=this[_0x1bc2a2(0x12d)](()=>this[_0x1bc2a2(0x11a)]()),_0x619706=this[_0x1bc2a2(0x12d)](()=>this['handleDownload']());if(_0x245b88[_0x1bc2a2(0x150)](_0x1bc2a2(0xfd))){_0x4a3fbc[_0x1bc2a2(0x11d)](this[_0x1bc2a2(0x114)](_0x1bc2a2(0x10c),_0x35602d));const _0x4a3e5c=this[_0x1bc2a2(0x114)](_0x1bc2a2(0xfa),_0x12e6fe);_0x4a3e5c[_0x1bc2a2(0x124)][_0x1bc2a2(0x12c)](_0x1bc2a2(0x121)),_0x51a46c[_0x1bc2a2(0x11d)](_0x4a3e5c);}else{if(_0x245b88[_0x1bc2a2(0x150)](_0x1bc2a2(0x133))){const _0x28deb4=this[_0x1bc2a2(0x114)](_0x1bc2a2(0xfa),_0x12e6fe);_0x28deb4['classList'][_0x1bc2a2(0x12c)](_0x1bc2a2(0x121)),_0x51a46c[_0x1bc2a2(0x11d)](_0x28deb4);}else{const _0x42f3d1=this[_0x1bc2a2(0x114)](_0x1bc2a2(0x129),_0x619706);_0x42f3d1[_0x1bc2a2(0x124)][_0x1bc2a2(0x12c)](_0x1bc2a2(0x121)),_0x51a46c['appendChild'](_0x42f3d1);}}_0x51a46c['appendChild'](this[_0x1bc2a2(0x114)](_0x1bc2a2(0xf5),_0x3aaa4a));const _0x274b3c=this[_0x1bc2a2(0x114)](_0x1bc2a2(0x112),_0x321f69);_0x274b3c[_0x1bc2a2(0x124)][_0x1bc2a2(0x12c)](_0x1bc2a2(0x11c)),_0x51a46c[_0x1bc2a2(0x11d)](_0x274b3c),this[_0x1bc2a2(0xf1)]['appendChild'](_0x4a3fbc);const _0x56628b=document[_0x1bc2a2(0xf0)](_0x1bc2a2(0x149));_0x56628b[_0x1bc2a2(0x14f)]=_0x1bc2a2(0xf3),this[_0x1bc2a2(0xf1)][_0x1bc2a2(0x11d)](_0x56628b),this[_0x1bc2a2(0xf1)][_0x1bc2a2(0x11d)](_0x51a46c);}[_0x461e4e(0x114)](_0x35165e,_0x1821a3){const _0x232820=_0x461e4e,_0x2d4e5f=document[_0x232820(0xf0)](_0x232820(0xea));return _0x2d4e5f[_0x232820(0x14f)]=_0x232820(0xea),_0x2d4e5f[_0x232820(0x135)]=_0x35165e,_0x2d4e5f[_0x232820(0x12f)]=async _0x30633a=>{const _0x3e5963=_0x232820,_0x40dd6f=_0x30633a['currentTarget'];if(_0x40dd6f[_0x3e5963(0x145)])return;_0x40dd6f['disabled']=!![];try{await _0x1821a3();}finally{_0x40dd6f[_0x3e5963(0x145)]=![];}},_0x2d4e5f;}async[_0x461e4e(0x152)](_0x47fc7c){const _0xbda947=_0x461e4e,_0x3ed065=await _0x47fc7c[_0xbda947(0x117)](),_0x1ae77f=document[_0xbda947(0xf0)](_0xbda947(0xee));_0x1ae77f['id']=_0xbda947(0xf8),_0x1ae77f[_0xbda947(0x135)]=_0x3ed065,_0x1ae77f[_0xbda947(0x108)]=!![],this[_0xbda947(0xff)][_0xbda947(0x11d)](_0x1ae77f);}async[_0x461e4e(0x134)](_0x440e2b){const _0x42111d=_0x461e4e,_0x19eba1=await _0x440e2b[_0x42111d(0x116)](),_0x406cd0=URL['createObjectURL'](_0x19eba1),_0x2b45ae=document[_0x42111d(0xf0)](_0x42111d(0x13d));_0x2b45ae['id']='imageViewer',_0x2b45ae[_0x42111d(0x11f)]=_0x406cd0,this[_0x42111d(0xff)][_0x42111d(0x11d)](_0x2b45ae);}async['handleFileContent'](_0x4beed2,_0x4a58a4){const _0x5a0b06=_0x461e4e,_0x69ff52=document[_0x5a0b06(0xf0)](_0x5a0b06(0x149));_0x69ff52[_0x5a0b06(0x14f)]=_0x5a0b06(0x146),_0x69ff52[_0x5a0b06(0x135)]=['文件类型:',_0x4a58a4][_0x5a0b06(0x14e)](''),this[_0x5a0b06(0xff)][_0x5a0b06(0x11d)](_0x69ff52);}['handleRaw'](){const _0x41500c=_0x461e4e;window[_0x41500c(0x10d)][_0x41500c(0x104)]=window[_0x41500c(0x10d)][_0x41500c(0x148)][_0x41500c(0x14d)]('/p/','/');}[_0x461e4e(0x14c)](){const _0x25ce27=_0x461e4e,_0x3e4de4=document[_0x25ce27(0x106)](_0x25ce27(0xf8))[_0x25ce27(0xfe)],_0x132cd5={'content':_0x3e4de4,'timestamp':Date[_0x25ce27(0x13b)](),'path':'/p'};localStorage['setItem'](this[_0x25ce27(0x12a)],JSON[_0x25ce27(0xf9)](_0x132cd5)),window[_0x25ce27(0x10d)]['href']='/p';}[_0x461e4e(0xf4)](){const _0x25ee7c=_0x461e4e;this[_0x25ee7c(0x130)](),window[_0x25ee7c(0x10d)][_0x25ee7c(0x104)]='/p';}[_0x461e4e(0x115)](){const _0x1d504d=_0x461e4e,_0x5f26f1=new Date()[_0x1d504d(0x137)](),_0x3e40c4=_0x5f26f1-this[_0x1d504d(0xed)];this[_0x1d504d(0x109)]?(clearTimeout(this['clickTimeout']),this[_0x1d504d(0x109)]=null,this[_0x1d504d(0x143)]()):this['clickTimeout']=setTimeout(()=>{const _0x542860=_0x1d504d;this[_0x542860(0x14a)](),this[_0x542860(0x109)]=null;},0xfa),this[_0x1d504d(0xed)]=_0x5f26f1;}async[_0x461e4e(0x143)](){const _0x2b6690=_0x461e4e;try{const _0x3e1780=window[_0x2b6690(0x10d)][_0x2b6690(0x104)];await navigator[_0x2b6690(0x151)][_0x2b6690(0x103)](_0x3e1780),this[_0x2b6690(0x140)](_0x2b6690(0x13e));}catch(_0x2018c5){console[_0x2b6690(0xe9)](_0x2b6690(0xf2),_0x2018c5),this[_0x2b6690(0x140)](_0x2b6690(0x120));}}async[_0x461e4e(0x14a)](){const _0x1178f4=_0x461e4e;try{let _0x45ed88='';const _0x28cb35=document[_0x1178f4(0x106)](_0x1178f4(0xf8)),_0x5ec267=document[_0x1178f4(0x106)](_0x1178f4(0x139));if(_0x28cb35)_0x45ed88=_0x28cb35[_0x1178f4(0xfe)];else _0x5ec267?_0x45ed88=_0x5ec267[_0x1178f4(0x11f)]:_0x45ed88=window[_0x1178f4(0x10d)][_0x1178f4(0x104)][_0x1178f4(0x14d)](_0x1178f4(0x105),'/');await navigator['clipboard']['writeText'](_0x45ed88),this[_0x1178f4(0x140)]('内容已复制到剪贴板');}catch(_0x114db5){console[_0x1178f4(0xe9)]('复制内容失败:',_0x114db5),this[_0x1178f4(0x140)](_0x1178f4(0x120));}}[_0x461e4e(0x140)](_0x441836){const _0x31aac4=_0x461e4e,_0xb91a00=document[_0x31aac4(0x125)](_0x31aac4(0x13f));_0xb91a00&&_0xb91a00['remove']();const _0x52b525=document[_0x31aac4(0xf0)](_0x31aac4(0x149));_0x52b525['className']='toast',_0x52b525['textContent']=_0x441836,document[_0x31aac4(0x128)]['appendChild'](_0x52b525),setTimeout(()=>{_0x52b525['remove']();},0xbb8);}async[_0x461e4e(0x11a)](){const _0x372f22=_0x461e4e,_0x115838=window[_0x372f22(0x10d)][_0x372f22(0x148)][_0x372f22(0x14d)](_0x372f22(0x105),_0x372f22(0x131));try{const _0x4756f8=await fetch(_0x115838,{'method':'DELETE'});if(_0x4756f8['ok'])this['clearLocalCache'](),window[_0x372f22(0x10d)][_0x372f22(0x104)]='/p';else{const _0x29bd29=await _0x4756f8[_0x372f22(0xf7)]();alert(_0x29bd29[_0x372f22(0xeb)]||'上传失败');}}catch(_0x31f283){alert(_0x31f283[_0x372f22(0xeb)]);}}[_0x461e4e(0x127)](){const _0x3dbe00=_0x461e4e;window[_0x3dbe00(0x10d)][_0x3dbe00(0x104)]=window[_0x3dbe00(0x10d)]['pathname'][_0x3dbe00(0x14d)]('/p/','/');}[_0x461e4e(0x130)](){const _0x71305c=_0x461e4e;localStorage[_0x71305c(0x10e)](this[_0x71305c(0x12a)]);}}new Viewer();
      </script>
  </body>
  </html>
 `;
    return html;
}

function getEditHtml() {
  const html = `
  <!DOCTYPE html>
  <html>
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
      <title>QBin</title>
      <style>
          .header{position:fixed;top:0;left:0;right:0;height:50px;background:rgba(255,255,255,.95);backdrop-filter:blur(5px);border-bottom:1px solid #eee;display:flex;align-items:center;justify-content:flex-end;padding:0 20px;z-index:100}body{margin:0;padding:0;height:100vh;display:flex;flex-direction:column;overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}.content{margin-top:50px;flex:1;display:flex;flex-direction:column;height:calc(100vh - 50px)}#editor{flex:1;width:100%;height:100%;padding:15px;border:none;resize:none;font-size:16px;box-sizing:border-box;-webkit-appearance:none;margin:0;line-height:1.6}#editor:focus{outline:0;border-color:#1890ff}#upload-btn{position:fixed;bottom:env(safe-area-inset-bottom,20px);right:20px;width:56px;height:56px;border-radius:50%;background:#1890ff;color:#fff;border:none;cursor:pointer;display:none;box-shadow:0 2px 8px rgba(0,0,0,.15);z-index:1000;transition:transform .2s}#upload-btn:active{background:#096dd9;transform:scale(.96)}.drag-over{border:2px dashed #1890ff!important}#password-input{width:140px;padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;-webkit-appearance:none}#password-input:focus{outline:0;border-color:#1890ff}@media (max-width:768px){.header{padding:0 15px}#password-input{width:120px}#editor{padding:12px;font-size:15px}}@supports (-webkit-touch-callout:none){#editor{touch-action:manipulation}#password-input{box-shadow:none}}
      </style>
  </head>
  <body>
      <div class="header">
          <input type="password" id="password-input" placeholder="可选：设置访问密码" autocomplete="off" />
      </div>
      <div class="content">
          <textarea id="editor" placeholder="请输入或粘贴内容..." spellcheck="false"></textarea>
      </div>
      <button id="upload-btn">上传</button>
      <script>
          const _0x3e5d9f=_0x31f6;function _0x31f6(_0x325e7a,_0x511001){const _0x1f4afb=_0x1f4a();return _0x31f6=function(_0x31f6cd,_0x3691a8){_0x31f6cd=_0x31f6cd-0x138;let _0x1c4bb7=_0x1f4afb[_0x31f6cd];return _0x1c4bb7;},_0x31f6(_0x325e7a,_0x511001);}(function(_0x20a090,_0x329cda){const _0x1fa21e=_0x31f6,_0x5186cf=_0x20a090();while(!![]){try{const _0x2ae917=parseInt(_0x1fa21e(0x198))/0x1*(-parseInt(_0x1fa21e(0x1b0))/0x2)+parseInt(_0x1fa21e(0x199))/0x3*(-parseInt(_0x1fa21e(0x160))/0x4)+parseInt(_0x1fa21e(0x166))/0x5*(-parseInt(_0x1fa21e(0x150))/0x6)+parseInt(_0x1fa21e(0x1b2))/0x7*(-parseInt(_0x1fa21e(0x174))/0x8)+-parseInt(_0x1fa21e(0x15d))/0x9*(-parseInt(_0x1fa21e(0x13f))/0xa)+-parseInt(_0x1fa21e(0x16c))/0xb*(parseInt(_0x1fa21e(0x1ab))/0xc)+-parseInt(_0x1fa21e(0x172))/0xd*(-parseInt(_0x1fa21e(0x178))/0xe);if(_0x2ae917===_0x329cda)break;else _0x5186cf['push'](_0x5186cf['shift']());}catch(_0x1655c0){_0x5186cf['push'](_0x5186cf['shift']());}}}(_0x1f4a,0x675bb));const editor=document[_0x3e5d9f(0x152)]('editor'),uploadBtn=document[_0x3e5d9f(0x152)]('upload-btn'),passwordInput=document[_0x3e5d9f(0x152)]('password-input');class PasteBoard{constructor(){const _0x18f7e4=_0x3e5d9f;this['currentPath']=this['parsePath'](window[_0x18f7e4(0x17d)][_0x18f7e4(0x186)]),this[_0x18f7e4(0x1a1)]=_0x18f7e4(0x176),this['isUploading']=![],this[_0x18f7e4(0x14b)]=null,this[_0x18f7e4(0x17b)](),this[_0x18f7e4(0x17f)](),this[_0x18f7e4(0x179)]();}['setupAutoSave'](){const _0x3aa10d=_0x3e5d9f;window['addEventListener'](_0x3aa10d(0x191),()=>{const _0x2d3ed4=_0x3aa10d;this[_0x2d3ed4(0x1b3)]();});}[_0x3e5d9f(0x1b3)](){const _0x587959=_0x3e5d9f,_0x45d648=editor[_0x587959(0x17c)],_0x38fada={'content':_0x45d648,'timestamp':Date[_0x587959(0x17a)](),'path':window[_0x587959(0x17d)]['pathname']};localStorage[_0x587959(0x1b4)](this[_0x587959(0x1a1)],JSON[_0x587959(0x158)](_0x38fada));}['loadFromLocalCache'](){const _0x4f7f7c=_0x3e5d9f;try{const _0x3396fd=localStorage['getItem'](this[_0x4f7f7c(0x1a1)]);if(_0x3396fd){const _0x4fbc02=JSON[_0x4f7f7c(0x155)](_0x3396fd),_0x5a46df=window[_0x4f7f7c(0x17d)]['pathname'],_0x21ed38=_0x5a46df==='/'||_0x5a46df==='/p',_0x53df8a=_0x5a46df===_0x4fbc02[_0x4f7f7c(0x141)];if(_0x21ed38||_0x53df8a)return editor[_0x4f7f7c(0x17c)]=_0x4fbc02['content'],!![];}return![];}catch(_0x150f79){return console[_0x4f7f7c(0x15e)]('Failed\x20to\x20load\x20from\x20cache:',_0x150f79),![];}}[_0x3e5d9f(0x1b8)](){const _0x5769b3=_0x3e5d9f;localStorage[_0x5769b3(0x1aa)](this[_0x5769b3(0x1a1)]);}[_0x3e5d9f(0x139)](_0x4c0e73,_0x1ce374){const _0xa75db7=_0x3e5d9f;return clearTimeout(this[_0xa75db7(0x14b)]),new Promise(_0x2abcf0=>{this['debounceTimeout']=setTimeout(()=>{_0x2abcf0(_0x4c0e73());},_0x1ce374);});}[_0x3e5d9f(0x164)](_0x47f331){const _0x139154=_0x3e5d9f,_0x228ba4=_0x47f331[_0x139154(0x143)]('/')['filter'](Boolean);if(_0x228ba4[_0x139154(0x1a8)]===0x0)return{'key':'','pwd':''};let _0x2795bf={'key':'','pwd':''};return _0x228ba4[0x0]==='p'?(_0x2795bf[_0x139154(0x1a0)]=_0x228ba4[0x1]||'',_0x2795bf['pwd']=_0x228ba4[0x2]||''):(_0x2795bf[_0x139154(0x1a0)]=_0x228ba4[0x0]||'',_0x2795bf[_0x139154(0x154)]=_0x228ba4[0x1]||''),_0x2795bf;}async[_0x3e5d9f(0x17f)](){const _0x4d7b7a=_0x3e5d9f,{key:_0x40fd91,pwd:_0x3560cb}=this[_0x4d7b7a(0x17e)];!_0x40fd91&&(this[_0x4d7b7a(0x1a3)]()&&(uploadBtn[_0x4d7b7a(0x16d)]['display']=editor[_0x4d7b7a(0x17c)][_0x4d7b7a(0x193)]()?'block':'none'));}[_0x3e5d9f(0x17b)](){const _0x2e2f31=_0x3e5d9f,_0x4d55b9=/iPad|iPhone|iPod/[_0x2e2f31(0x1a2)](navigator[_0x2e2f31(0x138)]);let _0x331f72;_0x4d55b9&&window[_0x2e2f31(0x19c)][_0x2e2f31(0x185)]('resize',()=>{const _0x3acaf1=_0x2e2f31,_0x637a87=window[_0x3acaf1(0x19c)][_0x3acaf1(0x16a)];uploadBtn['style'][_0x3acaf1(0x177)]=[Math[_0x3acaf1(0x1a6)](0x14,_0x637a87*0.05),'px']['join']('');}),editor[_0x2e2f31(0x185)](_0x2e2f31(0x14c),()=>{const _0x40b786=_0x2e2f31;uploadBtn[_0x40b786(0x16d)][_0x40b786(0x1ad)]=editor[_0x40b786(0x17c)]['trim']()?_0x40b786(0x161):'none',clearTimeout(_0x331f72),_0x331f72=setTimeout(()=>{this['saveToLocalCache']();},0x3e8);}),editor['addEventListener'](_0x2e2f31(0x190),_0x4bf79f=>{const _0x5b92b4=_0x2e2f31;if((_0x4bf79f[_0x5b92b4(0x1bb)]||_0x4bf79f['ctrlKey'])&&_0x4bf79f[_0x5b92b4(0x1a0)]===_0x5b92b4(0x175)){_0x4bf79f[_0x5b92b4(0x187)]();const _0x4599d4=editor[_0x5b92b4(0x17c)];console[_0x5b92b4(0x183)](_0x5b92b4(0x1af),_0x4599d4),this['handleUpload'](_0x4599d4,![]);}}),uploadBtn[_0x2e2f31(0x185)](_0x2e2f31(0x142),()=>{const _0x382cba=_0x2e2f31,_0xad3069=editor[_0x382cba(0x17c)];this[_0x382cba(0x1a7)](_0xad3069,![]);}),editor[_0x2e2f31(0x185)](_0x2e2f31(0x1b9),_0x458b9e=>{const _0x12e37e=_0x2e2f31,_0x2839f0=_0x458b9e['clipboardData'][_0x12e37e(0x19a)];for(let _0x510c62 of _0x2839f0){if(_0x510c62[_0x12e37e(0x13c)]['indexOf'](_0x12e37e(0x19e))===0x0){_0x458b9e[_0x12e37e(0x187)]();const _0x4acbba=_0x510c62[_0x12e37e(0x14e)]();this[_0x12e37e(0x1a7)](_0x4acbba,!![]);return;}}}),editor[_0x2e2f31(0x185)](_0x2e2f31(0x195),_0x52edb8=>{const _0x239675=_0x2e2f31;_0x52edb8[_0x239675(0x187)](),editor[_0x239675(0x146)][_0x239675(0x13b)](_0x239675(0x15a));}),editor[_0x2e2f31(0x185)](_0x2e2f31(0x167),()=>{const _0x29cc1b=_0x2e2f31;editor[_0x29cc1b(0x146)][_0x29cc1b(0x19f)](_0x29cc1b(0x15a));}),editor[_0x2e2f31(0x185)](_0x2e2f31(0x184),_0x18d044=>{const _0x617ceb=_0x2e2f31;_0x18d044[_0x617ceb(0x187)](),editor['classList'][_0x617ceb(0x19f)](_0x617ceb(0x15a));const _0xa03fb4=_0x18d044['dataTransfer'][_0x617ceb(0x14d)];if(_0xa03fb4[_0x617ceb(0x1a8)]>0x0){const _0x3b0f0f=_0xa03fb4[0x0];if(!_0x3b0f0f['type']){const _0xe9d3b1=this[_0x617ceb(0x18f)](_0x3b0f0f['name']);if(_0xe9d3b1){const _0x41786f=new File([_0x3b0f0f],_0x3b0f0f[_0x617ceb(0x189)],{'type':_0xe9d3b1});this[_0x617ceb(0x1a7)](_0x41786f,!![]);}else{const _0x353451=new File([_0x3b0f0f],_0x3b0f0f[_0x617ceb(0x189)],{'type':_0x617ceb(0x140)});this[_0x617ceb(0x1a7)](_0x353451,!![]);}}else this['handleUpload'](_0x3b0f0f,!![]);}});}[_0x3e5d9f(0x18f)](_0x283556){const _0x313e36=_0x3e5d9f,_0xbab387=_0x283556[_0x313e36(0x19d)]()[_0x313e36(0x143)]('.')[_0x313e36(0x194)](),_0x2bfa1e={'txt':_0x313e36(0x151),'pdf':_0x313e36(0x159),'doc':'application/msword','docx':_0x313e36(0x165),'xls':_0x313e36(0x1ae),'xlsx':_0x313e36(0x18e),'png':_0x313e36(0x180),'jpg':_0x313e36(0x1b5),'jpeg':_0x313e36(0x1b5),'gif':'image/gif','svg':_0x313e36(0x168),'mp3':_0x313e36(0x18b),'mp4':_0x313e36(0x171),'json':_0x313e36(0x149),'xml':_0x313e36(0x18c),'zip':_0x313e36(0x13e),'rar':_0x313e36(0x16f),'7z':_0x313e36(0x15f),'md':_0x313e36(0x15c),'csv':'text/csv','html':_0x313e36(0x16e),'css':_0x313e36(0x1a5),'js':_0x313e36(0x13a),'webp':_0x313e36(0x14f),'ppt':'application/vnd.ms-powerpoint','pptx':_0x313e36(0x1a9),'avi':_0x313e36(0x169),'wav':_0x313e36(0x197),'ogg':_0x313e36(0x156),'webm':'video/webm'};return _0x2bfa1e[_0xbab387]||null;}async[_0x3e5d9f(0x1a7)](_0x1d5e98,_0x12ef9c){const _0x2af8af=_0x3e5d9f;if(this[_0x2af8af(0x157)])return;if(!_0x1d5e98)return;if(_0x12ef9c&&!(_0x1d5e98 instanceof File))return;if(!_0x12ef9c&&!_0x1d5e98[_0x2af8af(0x193)]())return;try{this[_0x2af8af(0x157)]=!![],uploadBtn[_0x2af8af(0x15b)]=!![],await this['debounce'](async()=>{const _0x2e19fc=_0x2af8af,_0x18a902=passwordInput[_0x2e19fc(0x17c)][_0x2e19fc(0x193)]()||this[_0x2e19fc(0x17e)]['pwd'][_0x2e19fc(0x193)]();let _0x47b770=this[_0x2e19fc(0x17e)]['key']||API['generateKey']();try{const _0x4935d3=await API['uploadContent'](_0x1d5e98,_0x47b770,_0x18a902,_0x12ef9c);_0x4935d3&&(this[_0x2e19fc(0x1b8)](),window['location'][_0x2e19fc(0x170)]=_0x18a902?[_0x2e19fc(0x163),_0x47b770,'/',_0x18a902][_0x2e19fc(0x1b1)](''):['/p/',_0x47b770]['join'](''));}catch(_0x59c8ff){alert(_0x59c8ff[_0x2e19fc(0x182)]);}},0x5);}finally{this['isUploading']=![],uploadBtn[_0x2af8af(0x15b)]=![];}}}function _0x1f4a(){const _0x5d0de1=['application/vnd.ms-excel','content','17384uJsUqR','join','58583Zryhdn','saveToLocalCache','setItem','image/jpeg','请求失败','toString','clearLocalCache','paste','上传内容超出','metaKey','userAgent','debounce','text/javascript','add','type','服务器出错，请稍后重试','application/zip','20EMkWhD','application/octet-stream','path','click','split','PUT','MB限制','classList','random','headers','application/json','/s/','debounceTimeout','input','files','getAsFile','image/webp','2578626WsZkVo','text/plain','getElementById','无访问权限','pwd','parse','audio/ogg','isUploading','stringify','application/pdf','drag-over','disabled','text/markdown','2735613HNxtOM','error','application/x-7z-compressed','16OMVYsg','block','POST','/p/','parsePath','application/vnd.openxmlformats-officedocument.wordprocessingml.document','5fpsCJu','dragleave','image/svg+xml','video/x-msvideo','height','status','10879EFnTvh','style','text/html','application/x-rar-compressed','href','video/mp4','12280411DkslGj','includes','560bmngOX','Enter','pasteBoard_cache','bottom','42PHWKhg','setupAutoSave','now','initializeUI','value','location','currentPath','loadContent','image/png','json','message','log','drop','addEventListener','pathname','preventDefault','get','name','Content-Type','audio/mpeg','application/xml','getErrorMessageByStatus','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','getMimeTypeFromFileName','keydown','beforeunload','未授权访问','trim','pop','dragover','success','audio/wav','61uwLnWy','502956Uwlhvn','items','substring','visualViewport','toLowerCase','image/','remove','key','CACHE_KEY','test','loadFromLocalCache','上传失败:','text/css','max','handleUpload','length','application/vnd.openxmlformats-officedocument.presentationml.presentation','removeItem','9732MaLfjI','size','display'];_0x1f4a=function(){return _0x5d0de1;};return _0x1f4a();}const API={'generateKey'(){const _0x5d27ef=_0x3e5d9f;return Math[_0x5d27ef(0x147)]()[_0x5d27ef(0x1b7)](0x24)[_0x5d27ef(0x19b)](0x2,0xa);},async 'handleAPIError'(_0x258930){const _0x5484b4=_0x3e5d9f,_0x48e6a7=_0x258930[_0x5484b4(0x148)][_0x5484b4(0x188)]('Content-Type');if(_0x48e6a7?.[_0x5484b4(0x173)]('application/json'))try{const _0x5e9cbb=await _0x258930[_0x5484b4(0x181)]();return _0x5e9cbb[_0x5484b4(0x182)]||_0x5484b4(0x1b6);}catch{return this[_0x5484b4(0x18d)](_0x258930['status']);}return this[_0x5484b4(0x18d)](_0x258930[_0x5484b4(0x16b)]);},'getErrorMessageByStatus'(_0x487442){const _0x550bba=_0x3e5d9f;if(_0x487442>=0x1f4)return _0x550bba(0x13d);else{if(_0x487442===0x194)return'请求的资源不存在';else{if(_0x487442===0x193)return _0x550bba(0x153);else{if(_0x487442===0x191)return _0x550bba(0x192);else{if(_0x487442===0x190)return'请求参数错误';}}}}return _0x550bba(0x1b6);},async 'uploadContent'(_0x1e1d97,_0x28ea73,_0x3e6222='',_0x387a87=![]){const _0x3547e7=_0x3e5d9f;try{const _0x10712f=0x5*0x400*0x400,_0x3d556e=_0x387a87?_0x3547e7(0x144):_0x3547e7(0x162),_0x37ae2d=_0x3e6222?[_0x3547e7(0x14a),_0x28ea73,'/',_0x3e6222][_0x3547e7(0x1b1)](''):['/s/',_0x28ea73]['join']('');let _0x57d01b,_0x6852cc={};if(_0x1e1d97[_0x3547e7(0x1ac)]>_0x10712f)throw new Error([_0x3547e7(0x1ba),_0x10712f/0x400/0x400,_0x3547e7(0x145)]['join'](''));_0x387a87?(_0x57d01b=_0x1e1d97,_0x6852cc['Content-Type']=_0x1e1d97['type']||_0x3547e7(0x140)):(_0x57d01b=_0x1e1d97,_0x6852cc[_0x3547e7(0x18a)]=_0x3547e7(0x151));const _0x404570=await fetch(_0x37ae2d,{'method':_0x3d556e,'body':_0x57d01b,'headers':_0x6852cc});if(!_0x404570['ok']){const _0x4e8af5=await this['handleAPIError'](_0x404570);throw new Error(_0x4e8af5);}const _0x24404f=await _0x404570[_0x3547e7(0x181)]();return _0x24404f['status']===_0x3547e7(0x196);}catch(_0x453742){console[_0x3547e7(0x15e)](_0x3547e7(0x1a4),_0x453742);throw _0x453742;}}};new PasteBoard();
      </script>
  </body>
  </html>
  `;
  return html;
}

// html拦截界面
function getLoginPageHtml(): string {
  return `
  <!DOCTYPE html>
  <html lang="en">
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <link rel="icon" type="image/svg+xml" href="https://ik.imagekit.io/naihe/logo/qbin.svg">
      <title>QuickBin</title>
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
      <style>
          :root{--primary-color:#2563eb;--primary-hover:#1d4ed8;--background-color:#f8fafc;--container-bg:#ffffff;--text-color:#1e293b;--border-color:#e2e8f0;--error-color:#ef4444}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background-color:var(--background-color);display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;padding:1rem}.qbin-container{background-color:var(--container-bg);padding:2rem;border-radius:16px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);width:100%;max-width:420px}.qbin-header{text-align:center;margin-bottom:2rem;display:flex;flex-direction:column;align-items:center}.qbin-subtitle{color:#64748b;font-size:0.875rem;margin:0}.access-form{margin-top:1.5rem}.input-wrapper{position:relative;margin-bottom:1.5rem}.access-input{width:100%;padding:0.875rem 1rem 0.875rem 2.5rem;border:2px solid var(--border-color);border-radius:12px;font-size:1rem;transition:all 0.2s ease;box-sizing:border-box}.input-icon{position:absolute;left:1rem;top:50%;transform:translateY(-50%);color:#94a3b8}.access-input:focus{outline:none;border-color:var(--primary-color);box-shadow:0 0 0 3px rgba(37,99,235,0.1)}.access-button{background-color:var(--primary-color);color:white;border:none;padding:0.875rem;border-radius:12px;cursor:pointer;transition:all 0.2s ease;font-size:1rem;font-weight:600;width:100%;display:flex;align-items:center;justify-content:center;gap:0.5rem}.access-button:hover{background-color:var(--primary-hover);transform:translateY(-1px)}.access-button:active{transform:translateY(0)}.auth-divider{display:flex;align-items:center;text-align:center;margin:1.5rem 0;color:#64748b}.auth-divider::before,.auth-divider::after{content:'';flex:1;border-bottom:1px solid #e2e8f0}.auth-divider span{padding:0 1rem;font-size:0.875rem}.oauth-button{background-color:#ffffff;color:var(--text-color);border:2px solid var(--border-color);padding:0.875rem;border-radius:12px;cursor:pointer;transition:all 0.2s ease;font-size:1rem;font-weight:500;width:100%;display:flex;align-items:center;justify-content:center;gap:0.75rem;margin-bottom:1rem}.oauth-button:hover{background-color:#f8fafc;border-color:#94a3b8}.oauth-button img{width:20px;height:20px}.login-options{margin-bottom:1.5rem}.logo-svg{width:180px;height:40px;margin-bottom:0.5rem}.error-message{color:var(--error-color);font-size:0.875rem;margin-top:0.5rem;display:none}@media (max-width:480px){.qbin-container{padding:1.5rem}}
      </style>
  </head>
  <body>
      <div class="qbin-container">
          <div class="qbin-header">
              <img src="https://ik.imagekit.io/naihe/logo/qbin.svg" alt="QBin Logo">
              <p class="qbin-subtitle">Secure cloud QBin access</p>
          </div>
          <div class="login-options">
              <button onclick="handleOAuthLogin()" class="oauth-button">
                  <img src="https://ik.imagekit.io/naihe/logo/logo_do.png" alt="Linux.do Logo">
                  <span>Continue with Linux.do</span>
              </button>
          </div>
          <div class="auth-divider">
              <span>OR</span>
          </div>
          <form id="accessForm" class="access-form">
              <div class="input-wrapper">
                  <i class="fas fa-key input-icon"></i>
                  <input
                      type="password"
                      id="accessKey"
                      class="access-input"
                      required
                      placeholder="Enter access key"
                      autocomplete="current-password"
                  >
              </div>
              <p id="errorMessage" class="error-message">Invalid access key. Please try again.</p>
              <button type="submit" class="access-button">
                  <i class="fas fa-arrow-right"></i>
                  <span>Access QBin</span>
              </button>
          </form>
      </div>
      <script>
          function _0x1ae8(_0x243151,_0x3f824d){const _0x32f27b=_0x32f2();return _0x1ae8=function(_0x1ae847,_0x5d295f){_0x1ae847=_0x1ae847-0x7e;let _0x32d674=_0x32f27b[_0x1ae847];return _0x32d674;},_0x1ae8(_0x243151,_0x3f824d);}const _0x286d73=_0x1ae8;(function(_0x2610f0,_0x437886){const _0x40fde3=_0x1ae8,_0x16fef4=_0x2610f0();while(!![]){try{const _0x3af879=parseInt(_0x40fde3(0x9f))/0x1+parseInt(_0x40fde3(0x99))/0x2*(parseInt(_0x40fde3(0x9b))/0x3)+parseInt(_0x40fde3(0x8a))/0x4*(parseInt(_0x40fde3(0x97))/0x5)+-parseInt(_0x40fde3(0x95))/0x6+-parseInt(_0x40fde3(0x8c))/0x7+-parseInt(_0x40fde3(0x8b))/0x8*(-parseInt(_0x40fde3(0x9e))/0x9)+parseInt(_0x40fde3(0x92))/0xa;if(_0x3af879===_0x437886)break;else _0x16fef4['push'](_0x16fef4['shift']());}catch(_0x3aea9f){_0x16fef4['push'](_0x16fef4['shift']());}}}(_0x32f2,0xb9ca1));function _0x32f2(){const _0x4fd76c=['load','2064879ixTwSC','accessForm','get','7367697LMlIpI','1060560iXJXlv','search','addEventListener',';\x20path=/;\x20expires=','submit','href','/login','value','toUTCString','textContent','errorMessage','error_description','display','getElementById','36668mpCJyb','8YZAWdL','7655928bdTHjo','accessKey','location','Authentication\x20failed.\x20Please\x20try\x20again.','Failed\x20to\x20initialize\x20OAuth\x20login.\x20Please\x20try\x20again.','block','419770LvmmwJ','style','error','8768358NgHoGw','join','10dkjZCh','apikey=','4ltmcsO'];_0x32f2=function(){return _0x4fd76c;};return _0x32f2();}const accessForm=document['getElementById'](_0x286d73(0x9c)),errorMessage=document[_0x286d73(0x89)](_0x286d73(0x86));accessForm[_0x286d73(0x7e)](_0x286d73(0x80),_0x262fd7=>{const _0xf4842a=_0x286d73;_0x262fd7['preventDefault']();const _0x4c403c=document[_0xf4842a(0x89)](_0xf4842a(0x8d))[_0xf4842a(0x83)];if(_0x4c403c['trim']()===''){errorMessage[_0xf4842a(0x93)][_0xf4842a(0x88)]=_0xf4842a(0x91);return;}const _0x345165=new Date(Date['now']()+0x5265c00)[_0xf4842a(0x84)]();document['cookie']=[_0xf4842a(0x98),_0x4c403c,_0xf4842a(0x7f),_0x345165][_0xf4842a(0x96)](''),window[_0xf4842a(0x8e)][_0xf4842a(0x81)]='/p';});async function handleOAuthLogin(){const _0x1d3fcd=_0x286d73;try{window[_0x1d3fcd(0x8e)]['href']=_0x1d3fcd(0x82);}catch(_0x537756){console['error']('OAuth\x20login\x20error:',_0x537756),errorMessage[_0x1d3fcd(0x85)]=_0x1d3fcd(0x90),errorMessage[_0x1d3fcd(0x93)][_0x1d3fcd(0x88)]='block';}}window[_0x286d73(0x7e)](_0x286d73(0x9a),()=>{const _0x488080=_0x286d73,_0x407259=new URLSearchParams(window[_0x488080(0x8e)][_0x488080(0xa0)]),_0x22f45d=_0x407259[_0x488080(0x9d)](_0x488080(0x94)),_0x5eb424=_0x407259[_0x488080(0x9d)](_0x488080(0x87));_0x22f45d&&(errorMessage[_0x488080(0x85)]=_0x5eb424||_0x488080(0x8f),errorMessage[_0x488080(0x93)]['display']='block');});
      </script>
  </body>
  </html>
  `;
}

function generateKey(): string {
    return `${crypto.randomUUID().split('-').pop()}-${Date.now()}`;
}

const parsePath = (params) => {
  // 有效路径 < 3
  // 路径长度 2 < x < 32
  const isCommandPath = params.type === "p";
  let key, pwd;
  if (isCommandPath){
    if ((params.key.length > 32 || params.key.length < 2) || !VALID_CHARS_REGEX.test(params.key))
      return {key: null, pwd: null, render: null};
    if (params.pwd && (params.pwd.length > 32 || params.pwd.length < 2) || !VALID_CHARS_REGEX.test(params.pwd))
      return {key: null, pwd: null, render: null};
    key = params.key;
    pwd = params.pwd;
  }else{
    if ((params.type.length > 32 || params.type.length < 2) || !VALID_CHARS_REGEX.test(params.type))
      return {key: null, pwd: null, render: null};
    if (params.key && (params.key.length > 32 || params.key.length < 2) || !VALID_CHARS_REGEX.test(params.key))
      return {key: null, pwd: null, render: null};
    key = params.type;
    pwd = params.key;
  }
  return {
    key: key || generateKey(),
    pwd: pwd || '',
    render: isCommandPath
  };
};

// 从缓存中获取数据，如果缓存未命中，则从 KV 中获取并缓存
async function getCachedContent(key: string, pwd?: string): Promise<Metadata | null> {
  try {
    // 一级缓存：内存
    const memData = memCache.get(key);
    if (memData) {  // 有缓存
      if (memData.pwd){ // 有密码
        if(memData.pwd === pwd){  // 密码正确
          if(memData?.len){  // 有缓存真正数据
            return memData;
          }
        } else{ // 密码错误
          return null;
        }
      }
      else{ // 无密码
        if(memData?.len){ // 有缓存真正数据
          return memData;
        } else {   // 缓存错误信息
          return null;
        }
      }
    }

    // 二级缓存：Cache API
    const cacheKey = new Request(`http://dummy/p/${key}`);
    const cacheData = await cache.match(cacheKey);
    if (cacheData) {
        const headers = cacheData.headers;
        const metadata = {
            type: headers.get('Content-Type'),
            time: headers.get('x-time'),
            ip: headers.get('x-ip'),
            len: headers.get('Content-Length'),
            pwd: headers.get('x-pwd'),
        };
        if (!metadata.pwd || metadata.pwd === pwd) {
            console.log(`Cache hit (Cache API) ${key}`);
            metadata["content"] = await cacheData.arrayBuffer(),
            memCache.set(key, metadata);
            return metadata;
        }
        memCache.set(key, {'pwd': metadata.pwd});   // 减少内查询
    }

    // // 三级缓存：KV
    // console.log(`Cache miss, fetching from KV ${key}`);
    // const kvResult = await kv.get([PASTE_STORE, key]);
    // if (kvResult.value) {
    //   const metadata = kvResult.value as Metadata;
    //   if (!metadata.pwd || metadata.pwd === pwd) {
    //     await updateCache(key, metadata);
    //     return metadata;
    //   }
    // }

    return null;
  } catch (error) {
    console.error('Cache fetch error:', error);
    return null;
  }
}

// 更新缓存
async function updateCache(key: string, metadata: Metadata): Promise<void> {
  try {
    memCache.set(key, metadata); // 更新一级缓存
    const cacheKey = new Request(`http://dummy/p/${key}`);
    const header = {
      'Content-Type': metadata.type,
      'Content-Length': metadata.len,
      'x-time': metadata.time,
      'x-ip': metadata.ip,
      'x-pwd': metadata.pwd || "", // 避免输出 "undefined"
    }
    // if(metadata.len >= kvMAXSIZE){
    //   header['Cache-Control'] = 'max-age=2592000';
    // }
    await cache.put(cacheKey, new Response(metadata.content, { // 更新二级缓存
      headers: header,
    }));
  } catch (error) {
    console.error('Cache update error:', error);
  }
}

// 删除缓存
async function deleteCache(key: string, pwd: string) {
  try {
    memCache.set(key, {'pwd': pwd});    // 改用标记为空，减少查询消耗 memCache.delete(key)
    const cacheKey = new Request(`http://dummy/p/${key}`);
    await cache.delete(cacheKey); // 删除二级缓存
  } catch (error) {
    console.error('Cache deletion error:', error);
  }
}

async function handleContentUpload(ctx, key: string, pwd: string): Promise<Response> {
  // TODO 更新缓存？
  const request = ctx.request;
  const headers = request.headers;
  const clientIp = headers.get("cf-connecting-ip") || ctx.request.ip;
  console.log("POST", clientIp, request.url.pathname);

  try {
    let content: string;
    let contentType: string;
    let contentLength: number;

    if(!headers.get('Content-Length') && parseInt(headers.get('Content-Length')) > MAXSIZE){
        throw new PasteError(413, 'Content too large');
    }
    if(!headers.get('Content-Type') && (headers.get('Content-Type').length > 80 || !mimeTypeRegex.test(headers.get('Content-Type')))) {
        throw new PasteError(403, 'Invalid Content-Type format');
    }

    if (headers.get('Content-Type')?.includes('text/')) {
      content = (await request.body.text()).trim();
      contentType = 'text/plain; charset=utf-8';
      contentLength = new TextEncoder().encode(content).length;
    } else {
      // content = new Uint8Array(await request.arrayBuffer());
      content = await request.body.arrayBuffer();
      contentType = headers.get('Content-Type').trim();
      contentLength = content.byteLength;
    }

    if (contentLength > MAXSIZE) {
        throw new PasteError(413, 'Content too large');
    }

    const metadata: Metadata = {
        time: Date.now(),
        ip: clientIp,
        content,
        type: contentType,
        len: contentLength,
        pwd: pwd || undefined,
    };
    const res = await kv.atomic()
      .check({key: [PASTE_STORE, key], versionstamp: null})
      .set([PASTE_STORE, key], {
        ip: clientIp,
        len: contentLength,
        id: await ctx.state.session?.get("user")?.id,
        name: await ctx.state.session?.get("user")?.name,
      }, { expireIn: contentLength > kvMAXSIZE ? 2_592_000_000 : null })
      .commit();

    if (!res.ok) {
      throw new PasteError(409, 'Key already exists');
    }

    await updateCache(key, metadata);
    ctx.response.status = 200;
    ctx.response.headers.set('Content-Type', 'application/json');
    ctx.response.body = JSON.stringify({status: 'success', key});
  } catch (error) {
    console.error('Upload error:', error);
    if (error instanceof PasteError) {
      ctx.response.status = error.status;
      ctx.response.headers.set('Content-Type', 'application/json');
      ctx.response.body = JSON.stringify({status: 'error', message: error.message});
    } else {
      ctx.response.status = 500;
      ctx.response.headers.set('Content-Type', 'application/json');
      ctx.response.body = JSON.stringify({status: 'error', message: '内部服务器错误'});
    }
  }
}

// 通用错误处理中间件
app.use(async (ctx, next) => {
 try {
   await next();
 } catch (err) {
   console.log(err);
   const status = err instanceof PasteError ? err.status : 500;
   const message = err instanceof PasteError ? err.message : "内部服务器错误";

   ctx.response.status = status;
   Object.entries(HEADERS.JSON).forEach(([key, value]) => {
    ctx.response.headers.set(key, value);
   });
   ctx.response.body = { status: "error", message };
 }
});

app.use(Session.initMiddleware(store, {
  cookieSetOptions: {
    maxAge: 2592000000, // 30d后过期
    httpOnly: true,
    sameSite: "Lax"
    // secure: true,
  }
}))
// app.use(Session.initMiddleware(store))
// app.use(Session.initMiddleware(store, {
//   expireAfterSeconds: 900,  // 会话将在 15 分钟不活动后过期
// }));

// 认证中间件
app.use(async (ctx, next) => {
  const session = ctx.state.session;
  const isAuthenticated = await session?.get("user");
  const apikey = await ctx.cookies.get("apikey");
  const currentPath = ctx.request.url.pathname;
  const isAuthPath = ["/login", "/oauth2/callback"].includes(ctx.request.url.pathname);

  if ((isAuthenticated && isAuthenticated.level > 0) || apikey === "!!!/@@@") {  // 已认证
    Object.entries(HEADERS.HTML).forEach(([key, value]) => {
      ctx.response.headers.set(key, value);
    });
    await next();
    return;
  }

    // 公开路径，无需认证
  if (!isAuthenticated && isAuthPath) {
    // OAuth2 登录路由
    if(currentPath === "/login"){
      const { uri, codeVerifier } = await oauth2Client.code.getAuthorizationUri();
      ctx.state.session.flash("codeVerifier", codeVerifier);
      ctx.response.redirect(uri);
      return;
    }
    if (currentPath === "/oauth2/callback"){
      const codeVerifier = await ctx.state.session.get("codeVerifier");
      if (!codeVerifier) throw new Error("Invalid code verifier");

      const tokens = await oauth2Client.code.getToken(ctx.request.url, { codeVerifier });
      const userResponse = await fetch("https://connect.linux.do/api/user", {
        headers: { Authorization: `Bearer ${tokens.accessToken}` },
      });
      const userData = await userResponse.json();
      if (userData.active !== true) return ;
      await ctx.state.session.set("user", {
        'id': userData.id,
        'name': userData.username,
        'level': userData.trust_level,
        'apikey': userData.api_key,
      });
      // await storeDataInKV(userData, userData.id.toString());
      ctx.response.redirect("/");
      return;
    }
  }

  // 未认证用户重定向到登录页
  ctx.response.type = "text/html";
  ctx.response.body = getLoginPageHtml(); // 包含密码输入框和OAuth2登录按钮
});


router
 .get(["/", "/p"], async (ctx) => {
   ctx.response.headers.set("Content-Type", "text/html; charset=utf-8");
   // ctx.response.headers.set("Cache-Control", "public, max-age=86400");
   ctx.response.body = getEditHtml();
 })
 .get("/:type/:key?/:pwd?", async (ctx) => {
   const { key, pwd, render } = parsePath(ctx.params);
   if (key === null) {
     ctx.response.redirect("/");
     return;
   }
   console.log("GET", key, pwd);
   const metadata = await getCachedContent(key, pwd);
   if (!metadata) {
     ctx.response.body = getEditHtml();
     return;
   }
   if (render) {
     ctx.response.body = renderHtml(metadata);
   } else {
     ctx.response.headers.set('Content-Type', metadata.type);
     ctx.response.headers.set('Content-Length', metadata.len.toString());
     ctx.response.body = metadata.content;
   }
 })
 .post("/s/:key/:pwd?", async (ctx) => {
   const { key, pwd } = ctx.params;
   if (!key || keywords.has(key)) {
     throw new PasteError(403, "该KEY为保留字");
   }
   await handleContentUpload(ctx, key, pwd);
 })
 .put("/s/:key/:pwd?", async (ctx) => {
   const { key, pwd } = ctx.params;
   if (!key || keywords.has(key)) {
     throw new PasteError(403, "该KEY为保留字");
   }
   await handleContentUpload(ctx, key, pwd);
 })
 .delete("/d/:key/:pwd?", async (ctx) => {
   const { key, pwd } = ctx.params;
   if (!key || keywords.has(key)) {
     throw new PasteError(403, "该KEY为保留字");
   }

   const metadata = await getCachedContent(key, pwd);
   if (!metadata || (metadata.pwd && metadata.pwd !== pwd)) {
     throw new PasteError(403, "密码错误或内容不存在");
   }
   console.log("DEL", key, pwd);
   await Promise.all([
     kv.delete([PASTE_STORE, key]),
     deleteCache(key, pwd)
   ]);

   Object.entries(HEADERS.JSON).forEach(([key, value]) => {
       ctx.response.headers.set(key, value);
     });
   ctx.response.body = { status: "success", message: "删除成功" };
 });


app.use(router.routes());
app.use(router.allowedMethods());
await app.listen({ port: 8000 });

