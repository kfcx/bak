import{B as e,u as i}from"./useTable.5d27771c.js";import{T as o}from"./FormAction.9732afc1.js";import{a as s,d as t}from"./role.334f6c1b.js";import{u as r}from"./index.005634a4.js";import{R as n,c as a,s as d}from"./RoleDrawer.a7d34f10.js";import{_ as l,ai as m,f as c}from"./index.2956b203.js";import{A as p,a0 as u,B as f,D as j,w as h,aC as x,a5 as b,ad as w}from"./vendor.84d2d683.js";/* empty css              */import"./useForm.07071468.js";import"./useFormItem.75e32247.js";/* empty css               */import"./index.a66a0969.js";import"./useWindowSizeFn.a02e5cb7.js";import"./index.7a603658.js";/* empty css               *//* empty css               */import"./useContentViewHeight.fee9e617.js";/* empty css                *//* empty css                *//* empty css               *//* empty css               */import"./useSortable.817b3359.js";/* empty css                *//* empty css                *//* empty css                */import"./download.eecfd47d.js";import"./index.8bcb94a9.js";import"./index.1350911d.js";/* empty css               */import"./menu.17e77c51.js";const g=p({name:"RoleManagement",components:{BasicTable:e,RoleDrawer:n,TableAction:o},setup(){const{createMessage:e}=c(),{hasPermission:o}=m(),[n,{openDrawer:l}]=r(),[p,{reload:u}]=i({title:"角色列表",api:s,columns:a,formConfig:{labelWidth:120,schemas:d,fieldMapToTime:[["createTime",["createTimeStart","createTimeEnd"],"YYYY-MM-DD HH:mm:ss"]]},showTableSetting:!0,tableSetting:{redo:!0,size:!0,setting:!0,fullScreen:!0},useSearchForm:!0,bordered:!0,showIndexColumn:!1,canResize:!1,actionColumn:{width:150,title:"操作",dataIndex:"action",slots:{customRender:"action"},fixed:void 0}});return{hasPermission:o,registerTable:p,registerDrawer:n,handleCreate:function(){l(!0,{isUpdate:!0})},handleEdit:function(e){l(!0,{record:e,isUpdate:!0})},handleDelete:function(i){return o=this,s=null,r=function*(){t(i.id).then((()=>{e.success("已成功删除角色")})).catch((()=>{e.error("删除角色失败")})),yield u()},new Promise(((e,i)=>{var t=e=>{try{a(r.next(e))}catch(o){i(o)}},n=e=>{try{a(r.throw(e))}catch(o){i(o)}},a=i=>i.done?e(i.value):Promise.resolve(i.value).then(t,n);a((r=r.apply(o,s)).next())}));var o,s,r},handleSuccess:function(){u(),e.success("操作成功")}}}}),T=w(" 新增角色");var S=l(g,[["render",function(e,i,o,s,t,r){const n=u("a-button"),a=u("TableAction"),d=u("BasicTable"),l=u("RoleDrawer");return f(),j("div",null,[h(d,{onRegister:e.registerTable},x({action:b((({record:i})=>[h(a,{actions:[{icon:"clarity:note-edit-line",onClick:e.handleEdit.bind(null,i),ifShow:()=>e.hasPermission(["role_update"])},{icon:"ant-design:delete-outlined",color:"error",popConfirm:{title:"是否确认删除",placement:"left",confirm:e.handleDelete.bind(null,i)},ifShow:()=>e.hasPermission(["role_delete"])}]},null,8,["actions"])])),_:2},[e.hasPermission(["role_add"])?{name:"toolbar",fn:b((()=>[h(n,{type:"primary",onClick:e.handleCreate},{default:b((()=>[T])),_:1},8,["onClick"])]))}:void 0]),1032,["onRegister"]),h(l,{onRegister:e.registerDrawer,onSuccess:e.handleSuccess},null,8,["onRegister","onSuccess"])])}]]);export{S as default};
