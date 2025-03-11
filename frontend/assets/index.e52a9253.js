var e=Object.defineProperty,t=Object.defineProperties,a=Object.getOwnPropertyDescriptors,l=Object.getOwnPropertySymbols,r=Object.prototype.hasOwnProperty,n=Object.prototype.propertyIsEnumerable,s=(t,a,l)=>a in t?e(t,a,{enumerable:!0,configurable:!0,writable:!0,value:l}):t[a]=l,o=(e,t)=>{for(var a in t||(t={}))r.call(t,a)&&s(e,a,t[a]);if(l)for(var a of l(t))n.call(t,a)&&s(e,a,t[a]);return e},i=(e,l)=>t(e,a(l));import{a as p,ad as c,ae as u,af as d,h as f,w as b}from"./index.2956b203.js";import{A as m,r as y,k as v,u as O,w as j,a4 as x,bu as g,bv as h,bw as w}from"./vendor.84d2d683.js";/* empty css               */const P=b(m({name:"Description",props:{useCollapse:{type:Boolean,default:!0},title:{type:String,default:""},size:{type:String,validator:e=>["small","default","middle",void 0].includes(e),default:"small"},bordered:{type:Boolean,default:!0},column:{type:[Number,Object],default:()=>({xxl:4,xl:3,lg:3,md:3,sm:2,xs:1})},collapseOptions:{type:Object,default:null},schema:{type:Array,default:()=>[]},data:{type:Object}},emits:["register"],setup(e,{slots:t,emit:a}){const l=y(null),{prefixCls:r}=p("description"),n=c(),s=v((()=>o(o({},e),O(l)))),b=v((()=>i(o({},O(s)),{title:void 0}))),m=v((()=>!!O(s).title)),P=v((()=>o({canExpand:!1},O(b).collapseOptions))),S=v((()=>o(o({},O(n)),O(b))));function C({label:e,labelMinWidth:t,labelStyle:a}){if(!a&&!t)return e;const l=i(o({},a),{minWidth:`${t}px `});return j("div",{style:l},[e])}const D=()=>{let e;return j(g,x({class:`${r}`},O(S)),"function"==typeof(t=e=function(){const{schema:e,data:t}=O(b);return O(e).map((e=>{const{render:a,field:l,span:r,show:n,contentMinWidth:s}=e;if(n&&f(n)&&!n(t))return null;const o=()=>{var e;const t=null==(e=O(b))?void 0:e.data;if(!t)return null;const r=w(t,l);return f(a)?a(r,t):null!=r?r:""},i=s;return j(g.Item,{label:C(e),key:l,span:r},{default:()=>s?j("div",{style:{minWidth:`${i}px`}},[o()]):o()})})).filter((e=>!!e))}())||"[object Object]"===Object.prototype.toString.call(t)&&!h(t)?e:{default:()=>[e]});var t};return a("register",{setDescProps:function(e){l.value=o(o({},O(l)),e)}}),()=>O(m)?(()=>{const a=e.useCollapse?D():j("div",null,[D()]);if(!e.useCollapse)return a;const{canExpand:l,helpMessage:r}=O(P),{title:n}=O(s);return j(d,{title:n,canExpan:l,helpMessage:r},{default:()=>a,action:()=>u(t,"action")})})():D()}}));export{P as D};
