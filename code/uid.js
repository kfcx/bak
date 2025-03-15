//import 'https://prod.uidapi.com/static/js/uid2-sdk-1.0.0.js';
//document.write('<script src="https://cdn.prod.uidapi.com/uid2-sdk-3.2.0.js" type="text/javascript"></script>');
const CookiesData = (Cookies.get('4fourTV')) ? Cookies.get('4fourTV') : '';
window.__uid2 = window.__uid2 || {};
window.__uid2.callbacks = window.__uid2.callbacks || [];
//(3)呼叫API
const userEnCode = () => {
    return new Promise((resolve, reject) => {
        //if (data) {
        $.ajax({
            type: 'post',
            url: server4GTV + 'Account/GetUid2',
            data: {
                "clsIDENTITY_VALIDATE_ARUS": {
                    "fsVALUE": CookiesData
                }
            },
        }).done(function (result) {
            console.log(result);
            if (result.Success && result.Data) {
                resolve(result.Data);
            }
        }).fail(function (exception) {
            reject(exception.status);
            console.log('取得advertising_token失敗' + exception.status);
            //reject(exception);
        });
        //}
    });
}
if (CookiesData) {
    // 有沒有存取UID2
    let Uid2 = Cookies.get('uid2');
    if (Uid2) {
        //console.log(JSON.parse(Uid2));
        //console.log('有找到uid2');
        const uid = JSON.parse(Uid2).uid;
        const expires = JSON.parse(Uid2).expires;//給的資料是24H
        const time_12hr = 12 * 60 * 60 * 1000;// 12小時
        // 判斷是否登入超過一天
        if ((expires - Date.now()) >= time_12hr) {
            //console.log('在一天內');
            UID2Data.UID2 = uid;
        }
        // 重取advertising_token
        else {
            //console.log('超過一天重取API');
            userEnCode().then((res) => {
                // encode3次
                UID2Data.UID2 = res.advertising_token;
                //UID2Data.expires = res.identity_expires;
                //identity_expires
                Cookies.set('uid2', { 'uid': res.advertising_token, 'expires': res.identity_expires });
                window.__uid2.callbacks.push((eventType, payload) => {
                    if (eventType === "SdkLoaded") {
                        __uid2.init({ identity: res, cookieDomain: '4gtv.tv', useCookie: true});
                        //console.log(__uid2)
                    }
                });
            }).catch((err) => {
                console.log(err)
            });
        }


        //identity_expires - Date.now() > 12*60*60*1000
    }
    // 沒有
    else {
        //console.log('無uid2');
        // 取得advertising_token
        userEnCode().then((res) => {
            // encode3次
            UID2Data.UID2 = res.advertising_token;
            Cookies.set('uid2', { 'uid': res.advertising_token, 'expires': res.identity_expires });
            //console.log({'uid':res.advertising_token,'expires':res.identity_expires});        
            window.__uid2.callbacks.push((eventType, payload) => {
                if (eventType === "SdkLoaded") {
                    __uid2.init({ identity: res, cookieDomain: '4gtv.tv', useCookie: true });
                    //console.log(__uid2)
                }
            });
        }).catch((err) => {
            console.log(err)
        });
    }
} else {
    UID2Data.UID2 = '';
    Cookies.remove('uid2');
}


//uuid方法
var p_uuid = () => {
    let d = Date.now();
    if (typeof performance !== 'undefined' && typeof performance.now === 'function') {
        d += performance.now(); //use high-precision timer if available
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        let r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
}
let deviceid = Cookies.get('p_uuid');
if (!deviceid) {
    Cookies.set('p_uuid', p_uuid());
    deviceid = Cookies.get('p_uuid');
}


//https://eb0bb528fd60483e9db10bece15ffccd.mediatailor.ap-southeast-1.amazonaws.com/v1/master/50bc07a2b4601aa7bb1dac8f09af1d7078560ccf/4gtvfree_ctv/r2sX3q1RrnWJ1bhah2HVcLm2PE5MVktBDpkQUJkYhbM%3d/master.m3u8?token=MSiJIpruYHEHwjzhiZlvBg&expires=1647528416&token1=9JEphyJzbF1jRiBQU8YUAg&expires1=1647528416&refer=MDE2MmNmMTktZWI4YS00NWIxLTg2NWYtZjAzODdiY2QxZjVh&y=0&ads.cust_params=adid%253D[adid]%2526ip%253D61.216.147.98%2526ua%253D[user-agent]%2526is_lat%253D[is-lat]%2526appname%253D[appname]%2526vtitle=[vtitle]%2526assetid=[assetid]%2526originid=4gtvfree_ctv&ads.correlator=[timestamp]&

String.prototype.SetUrlParams = function SetUrlParams(times) {
    //let converTag = this.toLowerCase();
    let converTag = this;
    let vtitle = UID2Data.vtitle ? UID2Data.vtitle : '', uid2 = UID2Data.UID2 ? UID2Data.UID2 : '';
    // 可能由於 display:block 改成 display:flex 的關係，jquery 的 height 抓到的值都是 0，所以改用 css 的 height，但要記得去掉尾巴的 px
    let playerwidth = $(Param.PlayerContainer).parent().css('width').replace(/px/g, '');//撥放器的TAG PLAYER_CONTAINER_TAG
    let playerheight = $(Param.PlayerContainer).parent().css('height').replace(/px/g, '');//撥放器的TAG
    for (let i = 0, code = times; i < code; i++) {
        vtitle = encodeURIComponent(vtitle);
        uid2 = encodeURIComponent(uid2);
    }
    //console.log(times + '次（vtitle）：' + vtitle + '  （UID2）' + uid2);
    converTag = converTag.replace(/\[timestamp\]/g, Date.now());
    converTag = converTag.replace(/\[playerwidth\]/g, Math.round(playerwidth));
    converTag = converTag.replace(/\[playerheight\]/g, Math.round(playerheight));
    converTag = converTag.replace(/\[pageurl\]/g, encodeURIComponent(document.URL));
    converTag = converTag.replace(/\[urlencodedpageurl\]/g, encodeURIComponent(document.URL));
    converTag = converTag.replace(/\[referrer_url\]/g, encodeURIComponent(document.URL));
    converTag = converTag.replace(/\[description_url\]/g, encodeURIComponent(document.URL));
    converTag = converTag.replace(/\[referrer_url\]/g, encodeURIComponent(document.URL));
    converTag = converTag.replace(/\[is-lat\]/g, 0);//自定義使用者是否允許廣告追蹤 0|1
    converTag = converTag.replace(/\[assetid\]/g, UID2Data.assetid);//Asset ID || VOD_NO
    converTag = converTag.replace(/\[deviceid\]/g, deviceid);//每個瀏覽器獨特的UUID(自己產生存cookie)UUID
    converTag = converTag.replace(/\[vtitle\]/g, vtitle);//頻道名稱|VOD主檔名稱TITILE
    converTag = converTag.replace(/\[vtype\]/g, UID2Data.vtype);//live|vod
    converTag = converTag.replace(/\[vkind\]/g, encodeURIComponent(UID2Data.vkind));//頻道類別(fsTYPE_NAME)| VOD館別TYPE(中文)
    converTag = converTag.replace(/\[uid2\]/g, uid2);//用使用者的email打新的API取得的token(GetURL時就要重取)UID2
    converTag = converTag.replace(/\[uid2_e1\]/g, encodeURIComponent(UID2Data.UID2 ? UID2Data.UID2 : ''));
    return converTag;
}
//console.log(list);
var EventLogTrack = (data) => {
    //console.log('EventLogTrack:', data);
    let source;
    (data.event === 'play_alive') ? source = '&Memo=' + data.Memo : source = '&Category=' + data.Category;
    let contentID = ($('#Hidden_Asset_ID')[0]) ? $('#Hidden_Asset_ID').val() : data.ContentID;
    const VodNo = (dataLayerObj.VodNo) ? '&VodNo=' + dataLayerObj.VodNo:'';
    const Episode = (data.Category === 'channel' || data.Category === 'livevod') ? '' : '&Episode=' + data.Episode;
    const url = 'https://collect.4gtv.tv/EventLog/' + data.event.replace('_', '') + '?ContentID=' + contentID + Episode + source + '&DeviceMode=' + GAMode + VodNo +'&AID=' + Cookies.get("Account_ID") + '&ref_url=' + location.href;
    //new Promise(function (resolve, reject) {
    $.get(url, function (v) {
    }).fail(function (error) {
        console.log('EventLog_error:'+error);
    }).always(function (v) {
        console.log({ name: 'EventLogTrack結果:' + data.event + '_' + v, _url: url });
    });
    //});
    //.then((v) => {
    //    console.debug({ name: 'EventLogTrack結果:' + data.event + '_' + v, _url: url});
    //});
}
