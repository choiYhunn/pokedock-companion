#!/usr/bin/env node
// Local, offline ED25519 asset pack signing and verification helper.
// No network access, no copyrighted resources included.
// Usage: node assets.cjs sign <directory> <version> <private_key_pem_path>
//        node assets.cjs verify <directory> <trusted_public_key_pem_path>
"use strict";
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
const MAX_FILES=2000,MAX_FILE=8*1024*1024,MAX_PACK=96*1024*1024;
const EXT=new Set([".png",".webp",".wav",".ogg",".json"]);
function scan(root){const files=[];function walk(rel){for(const entry of fs.readdirSync(path.join(root,rel),{withFileTypes:true})){
 if(!/^[A-Za-z0-9_-][A-Za-z0-9_.-]*$/.test(entry.name)||entry.name.startsWith("."))throw Error("invalid path");
 const local=rel?rel+"/"+entry.name:entry.name;if(local==="manifest.json"||local==="manifest.sig")continue;
 const absolute=path.join(root,local);const st=fs.lstatSync(absolute);
 if(st.isSymbolicLink())throw Error("symlink rejected");if(st.isDirectory()){walk(local);continue;}
 if(!st.isFile()||!EXT.has(path.extname(local).toLowerCase()))throw Error("unsupported asset: "+local);
 if(st.size>MAX_FILE)throw Error("file too large: "+local);
 files.push({path:local,bytes:st.size,sha256:crypto.createHash("sha256").update(fs.readFileSync(absolute)).digest("hex")});
 if(files.length>MAX_FILES)throw Error("too many assets");
 }}walk("");files.sort((a,b)=>a.path.localeCompare(b.path));let total=files.reduce((s,f)=>s+f.bytes,0);if(total>MAX_PACK)throw Error("pack too large");if(!files.length)throw Error("empty pack");return {files,total};}
function signPack(root,version,keyPath){if(!/^[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$/.test(version))throw Error("invalid version");
 const {files,total}=scan(root);const manifest={schema:1,target:"ghost-v16",asset_api:1,version,totalBytes:total,files};
 const bytes=Buffer.from(JSON.stringify(manifest));const sig=crypto.sign(null,bytes,fs.readFileSync(keyPath));
 fs.writeFileSync(path.join(root,"manifest.json"),bytes);fs.writeFileSync(path.join(root,"manifest.sig"),sig.toString("base64")+"\n");
 return manifest;}
function verifyPack(root,pubPath){const bytes=fs.readFileSync(path.join(root,"manifest.json"));
 const sig=Buffer.from(fs.readFileSync(path.join(root,"manifest.sig"),"utf8").trim(),"base64");
 if(!crypto.verify(null,bytes,fs.readFileSync(pubPath),sig))throw Error("signature invalid");
 const manifest=JSON.parse(bytes.toString("utf8"));
 if(manifest.schema!==1||manifest.target!=="ghost-v16"||manifest.asset_api!==1)throw Error("contract mismatch");
 const {files,total}=scan(root);if(JSON.stringify(files)!==JSON.stringify(manifest.files)||total!==manifest.totalBytes)throw Error("file hash/size mismatch");
 return manifest;}
if(require.main===module){try{const [cmd,root,arg,keyPath]=process.argv.slice(2);if(!root)throw Error("root required");
 let m;if(cmd==="sign"){if(!keyPath)throw Error("version/private key required");m=signPack(root,arg,keyPath);}
 else if(cmd==="verify"){if(!arg)throw Error("trusted public key required");m=verifyPack(root,arg);}
 else throw Error("usage: sign <root> <version> <private.pem> | verify <root> <public.pem>");
 console.log("V16 asset pack",cmd,"PASS",m.version,m.files.length+" files");}
 catch(e){console.error(e.message);process.exitCode=1;}}
module.exports={scan,signPack,verifyPack};
