var e,n,t=(e,n,t)=>new Promise(((u,r)=>{var s=e=>{try{l(t.next(e))}catch(n){r(n)}},a=e=>{try{l(t.throw(e))}catch(n){r(n)}},l=e=>e.done?u(e.value):Promise.resolve(e.value).then(s,a);l((t=t.apply(e,n)).next())}));import{aD as u}from"./index.2956b203.js";(n=e||(e={})).MenuTree="/access/menu/tree",n.MenuList="/access/menu/list",n.MenuUpdate="/access/menu",n.MenuDetail="/access/menu";const r=n=>t(this,null,(function*(){return yield u.get({url:`${e.MenuDetail}/${n}`})})),s=n=>t(this,null,(function*(){return yield u.get({url:e.MenuTree,params:n})})),a=()=>t(this,null,(function*(){return yield u.get({url:e.MenuList})})),l=n=>t(this,null,(function*(){return yield u.post({url:e.MenuUpdate,params:n})})),i=(n,r)=>t(this,null,(function*(){return yield u.put({url:`${e.MenuUpdate}/${n}`,params:r})})),c=n=>t(this,null,(function*(){return yield u.delete({url:`${e.MenuUpdate}/${n}`})}));export{s as a,l as c,c as d,a as g,i as p,r};
