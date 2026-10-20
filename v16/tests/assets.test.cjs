const fs=require("node:fs"),path=require("node:path"),os=require("node:os"),crypto=require("node:crypto"),assert=require("node:assert/strict");
const {signPack,verifyPack}=require("../tools/assets.cjs");
const root=fs.mkdtempSync(path.join(os.tmpdir(),"ghost-v16-test-"));
try{
 const {publicKey,privateKey}=crypto.generateKeyPairSync("ed25519");
 const pub=path.join(root,"pub.pem"),priv=path.join(root,"priv.pem"),pack=path.join(root,"pack");
 fs.writeFileSync(pub,publicKey.export({type:"spki",format:"pem"}));fs.writeFileSync(priv,privateKey.export({type:"pkcs8",format:"pem"}));
 fs.mkdirSync(pack);fs.writeFileSync(path.join(pack,"idle.ghf"),Buffer.from([71,72,70,49,1,0,1,0,1,0,0,0,0xC0,0,0]));
 const m=signPack(pack,"1.0.0",priv);assert.equal(m.files.length,1);
 assert.equal(verifyPack(pack,pub).version,"1.0.0");
 fs.writeFileSync(path.join(pack,"idle.ghf"),"corrupted");
 assert.throws(()=>verifyPack(pack,pub),/hash\/size mismatch/);
 console.log("V16 asset signature + tamper detection PASS");
} finally {fs.rmSync(root,{recursive:true,force:true});}
