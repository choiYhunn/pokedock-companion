// Prepare single-root WebView content from the faithfully preserved original V10 UI.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../..'),mobile=path.resolve(__dirname,'..'),target=path.join(mobile,'www');
fs.rmSync(target,{recursive:true,force:true});fs.mkdirSync(path.join(target,'ui'),{recursive:true});
for(const file of ['index.html','manifest.webmanifest','icon.svg','sw.js']) {
 let txt=fs.readFileSync(path.join(mobile,file),'utf8').replaceAll('../ui/','./ui/');
 fs.writeFileSync(path.join(target,file),txt);
}
for(const file of ['party-game.css','party-game.js']) fs.copyFileSync(path.join(root,'ui',file),path.join(target,'ui',file));
console.log('Faithful V10 mobile bundle prepared:',target,'(not a compiled APK/IPA)');
