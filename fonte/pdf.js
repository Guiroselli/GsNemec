const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://'+process.argv[2]+'/index.html');
const mins=await p.evaluate(()=>Math.min(...[...document.querySelectorAll('body *')].filter(e=>e.childNodes.length&&[...e.childNodes].some(n=>n.nodeType==3&&n.textContent.trim())).map(e=>parseFloat(getComputedStyle(e).fontSize)*0.75)));
console.log('min pt',mins,'height cm',document=await p.evaluate(()=>document.body.scrollHeight/37.8));
await p.pdf({path:process.argv[2]+'/GS_CitizenTech.pdf',format:'A4',margin:{top:'1.5cm',bottom:'1.5cm',left:'1.5cm',right:'1.5cm'},printBackground:true});await b.close()})()
