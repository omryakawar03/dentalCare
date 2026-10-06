"use client";
import { useState } from "react";

const copy = {
  mr: { name: "डिजिटल नगर पालिका", sub: "आपल्या नगरपालिकेच्या सेवा, आता एका ठिकाणी", greeting: "नमस्कार!", ward: "आपला प्रभाग", actions: ["तक्रार नोंदवा", "माझ्या तक्रारी", "नागरी सेवा", "बातम्या व सूचना", "आपत्कालीन संपर्क", "योजना"], notice: "पाणीपुरवठा व नागरी सेवांबद्दल अधिकृत सूचना येथे पहा.", login: "मोबाईलने पुढे जा", services: "लोकप्रिय सेवा", emergency: "आपत्कालीन क्रमांक स्थानिक प्रशासनाकडून पडताळल्यानंतर येथे उपलब्ध होतील." },
  hi: { name: "डिजिटल नगर पालिका", sub: "आपकी नगरपालिका सेवाएँ, एक ही जगह", greeting: "नमस्कार!", ward: "आपका वार्ड", actions: ["शिकायत दर्ज करें", "मेरी शिकायतें", "नागरिक सेवाएँ", "समाचार और सूचनाएँ", "आपातकालीन संपर्क", "योजनाएँ"], notice: "पानी और नागरिक सेवाओं की आधिकारिक सूचनाएँ यहाँ देखें।", login: "मोबाइल से आगे बढ़ें", services: "लोकप्रिय सेवाएँ", emergency: "स्थानीय प्रशासन से सत्यापित होने के बाद आपातकालीन नंबर यहाँ दिखेंगे." },
  en: { name: "Digital Nagar Palika", sub: "Municipal services, all in one place", greeting: "Namaskar!", ward: "Your ward", actions: ["Raise a complaint", "My complaints", "Municipal services", "News & notices", "Emergency contacts", "Schemes"], notice: "Official updates on water supply and civic services appear here.", login: "Continue with mobile", services: "Popular services", emergency: "Emergency numbers will appear here after verification by the local administration." },
};
export default function Home() {
  const [locale, setLocale] = useState<keyof typeof copy>("mr"); const t = copy[locale];
  return <main className="shell"><header className="top"><div className="brand"><span className="seal" aria-hidden="true">न</span><div><strong>{t.name}</strong><small>{t.sub}</small></div></div><label className="locale">{locale === "mr" ? "भाषा" : locale === "hi" ? "भाषा" : "Language"}<select aria-label="Language" value={locale} onChange={e => setLocale(e.target.value as keyof typeof copy)}><option value="mr">मराठी</option><option value="hi">हिन्दी</option><option value="en">English</option></select></label></header>
    <section className="welcome"><div><p className="eyebrow">CITIZEN SERVICES</p><h1>{t.greeting}</h1><p>{t.ward}: <b>—</b></p><p className="muted">Sign in to view your personal services and household information.</p><button className="primary">{t.login}</button></div><div className="notice"><span aria-hidden="true">◉</span><div><b>सूचना · Notice</b><p>{t.notice}</p></div></div></section>
    <section aria-labelledby="quick-title"><h2 id="quick-title">{locale === "mr" ? "आपल्याला काय हवे आहे?" : locale === "hi" ? "आप क्या करना चाहते हैं?" : "What would you like to do?"}</h2><div className="grid">{t.actions.map((item,i)=><button className="action" key={item}><span aria-hidden="true" className="icon">{["＋","◷","▤","▣","☎","✿"][i]}</span><span>{item}</span><span aria-hidden="true" className="arrow">›</span></button>)}</div></section>
    <section className="service"><h2>{t.services}</h2><div className="service-row"><article><b>Property tax</b><p>Request / Application</p></article><article><b>Water connection</b><p>Request / Application</p></article><article><b>Birth &amp; death records</b><p>Request / Application</p></article></div></section>
    <footer><p>{t.emergency}</p><small>Official information only · Privacy · Accessibility · Help</small></footer>
  </main>;
}
