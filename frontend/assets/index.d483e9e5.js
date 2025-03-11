import{bA as t,b8 as e,b7 as a,c1 as i,bu as s,a0 as n,B as o,D as r,w as l,a5 as d,H as m,J as u,K as c,a1 as p,ac as f,ad as h}from"./vendor.84d2d683.js";/* empty css                *//* empty css                *//* empty css               *//* empty css               *//* empty css               */import v from"./statusCard.d9341de9.js";import{aD as b,_ as C,ah as y,b as _}from"./index.2956b203.js";import D from"./echartCard.393143c8.js";/* empty css                */import"./lineEchart.bf56ee1b.js";import"./echarts.3fd60ded.js";import"./VisitAnalysisBar.57c80667.js";import"./useECharts.39b9c245.js";import"./props.f48aca0b.js";var I;(I||(I={})).serverInfo="/system/monitor";const g={name:"MonitorPage",components:{AButton:y,EchartCard:D,LyStatuscard:v,InputNumber:t,ARow:e,ACol:a,Card:i,ADescriptions:s,ADescriptionsItem:s.Item},data:()=>({t:void 0,isFull:!1,isRunning:!1,showloading:!0,tableHeight:"500px",monitorData:{os:{hostname:"",ip:"",system:"",machine:""},usedcpu:{user:0,system:0,idle:0,interrupt:0,dpc:0,total:0},infocpu:[0,0,[0,0,0,0],"",0,1],disk:[{path:"",size:["0GB","0GB","0GB",0],inodes:!1}],is_windows:!0,mem:{percent:0,total:0,free:0,used:0},system:"",time:"0day",network:{up:0,down:0,downTotal:0,upTotal:0,network:{}}},refreshInterval:3,iconClass:"",timer:null}),watch:{isFull:function(){this.listenResize()}},created(){this.getData();const{t:t}=_();this.t=t},mounted(){this.isRunning||(this.intervalMonitor(),this.isRunning=!0,setTimeout((()=>{this.showloading=!1}),2e3)),window.addEventListener("resize",this.listenResize),this.listenResize()},activated(){this.isRunning||(this.intervalMonitor(),this.isRunning=!0)},deactivated(){this.isRunning=!1,this.clearIntervalMonitor()},unmounted(){this.clearIntervalMonitor(),window.removeEventListener("resize",this.listenResize)},methods:{setFull(){this.isFull=!this.isFull},getData(){b.get({url:I.serverInfo}).then((t=>{this.monitorData=t;let e=t.system.split(" ")[0].toLowerCase();this.iconClass="ico-"+e}))},intervalMonitor(){let t=this;this.timer=setInterval((()=>{t.getData()}),1e3*t.refreshInterval)},restartIntervalMonitor(){this.clearIntervalMonitor(),this.intervalMonitor()},clearIntervalMonitor(){clearInterval(this.timer),this.timer=null},handleResize(){},listenResize(){},getTheTableHeight(){}}},x={class:"p-4"},k={style:{"font-size":"13px"}};var w=C(g,[["render",function(t,e,a,i,s,v){const b=n("ACol"),C=n("InputNumber"),y=n("a-button"),_=n("ARow"),D=n("Card"),I=n("ly-statuscard"),g=n("EchartCard"),w=n("a-descriptions-item"),j=n("a-descriptions");return o(),r("div",x,[l(D,{justify:"center",size:"small"},{default:d((()=>[l(_,{type:"flex",justify:"center"},{default:d((()=>[l(b,{span:2},{default:d((()=>[m("span",{class:c(s.iconClass)},u(s.t("common.monitor.osText"))+"：",3)])),_:1}),l(b,{span:8},{default:d((()=>[m("div",null,u(s.monitorData.system),1)])),_:1}),l(b,{span:4},{default:d((()=>[m("div",null,u(s.t("common.monitor.autoRefreshText"))+"：",1)])),_:1}),l(b,{span:4},{default:d((()=>[l(C,{value:s.refreshInterval,"onUpdate:value":e[0]||(e[0]=t=>s.refreshInterval=t),size:"small",min:3,onChange:v.restartIntervalMonitor},null,8,["value","onChange"])])),_:1}),l(b,{span:5},{default:d((()=>[s.timer?(o(),p(y,{key:0,style:{"margin-left":"20px"},type:"link",text:!0,link:"",onClick:v.getData},{default:d((()=>[m("div",{style:{"font-size":"13px"},onClick:e[1]||(e[1]=(...t)=>v.clearIntervalMonitor&&v.clearIntervalMonitor(...t))},u(s.t("common.monitor.stopText")),1)])),_:1},8,["onClick"])):f("",!0),null==s.timer?(o(),p(y,{key:1,style:{"margin-left":"20px"},type:"link",text:!0,link:"",onClick:v.getData},{default:d((()=>[m("div",{style:{"font-size":"13px"},onClick:e[2]||(e[2]=(...t)=>v.restartIntervalMonitor&&v.restartIntervalMonitor(...t))},u(s.t("common.monitor.startText")),1)])),_:1},8,["onClick"])):f("",!0),l(y,{type:"link",text:!0,link:"",onClick:v.getData},{default:d((()=>[m("div",k,u(s.t("common.monitor.manualRefreshText")),1)])),_:1},8,["onClick"])])),_:1})])),_:1})])),_:1}),m("div",null,[l(I,{modelValue:s.monitorData,"onUpdate:modelValue":e[3]||(e[3]=t=>s.monitorData=t),class:"!my-4 enter-y"},null,8,["modelValue"])]),m("div",null,[l(g,{network:s.monitorData.network,class:"!my-4 enter-y"},null,8,["network"])]),l(D,{title:"CPU监控",bordered:!1,class:"mb-2"},{default:d((()=>[l(j,{size:"middle",column:2,bordered:""},{default:d((()=>[l(w,{label:"CPU名称"},{default:d((()=>[h(u(s.monitorData.infocpu[3]),1)])),_:1}),l(w,{label:"CPU数量"},{default:d((()=>[h(u(s.monitorData.infocpu[5])+"颗物理CPU",1)])),_:1}),l(w,{label:"CPU物理核心数"},{default:d((()=>[h(u(s.monitorData.infocpu[5]*s.monitorData.infocpu[4])+"个物理核心",1)])),_:1}),l(w,{label:"CPU逻辑核心数"},{default:d((()=>[h(u(s.monitorData.infocpu[1])+"个逻辑核心",1)])),_:1})])),_:1})])),_:1}),l(D,{title:"服务器信息",bordered:!1,class:"mb-2"},{default:d((()=>[l(j,{size:"middle",column:2,bordered:""},{default:d((()=>[l(w,{label:"服务器名称"},{default:d((()=>[h(u(s.monitorData.os.hostname),1)])),_:1}),l(w,{label:"服务器操作系统"},{default:d((()=>[h(u(s.monitorData.os.system),1)])),_:1}),l(w,{label:"服务器IP"},{default:d((()=>[h(u(s.monitorData.os.ip),1)])),_:1}),l(w,{label:"服务器架构"},{default:d((()=>[h(u(s.monitorData.os.machine),1)])),_:1})])),_:1})])),_:1})])}],["__scopeId","data-v-f4b8db4c"]]);export{w as default};
