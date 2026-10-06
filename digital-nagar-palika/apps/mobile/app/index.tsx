import { useState } from 'react';
import { Pressable, SafeAreaView, ScrollView, Text, View } from 'react-native';
const strings = {
  mr: { title: 'डिजिटल नगर पालिका', subtitle: 'नागरी सेवा, आता एका ठिकाणी', hello: 'नमस्कार!', actions: ['तक्रार नोंदवा', 'माझ्या तक्रारी', 'नागरी सेवा', 'बातम्या व सूचना', 'आपत्कालीन संपर्क', 'योजना'], language: 'भाषा' },
  hi: { title: 'डिजिटल नगर पालिका', subtitle: 'नागरिक सेवाएँ, एक ही जगह', hello: 'नमस्कार!', actions: ['शिकायत दर्ज करें', 'मेरी शिकायतें', 'नागरिक सेवाएँ', 'समाचार और सूचनाएँ', 'आपातकालीन संपर्क', 'योजनाएँ'], language: 'भाषा' },
  en: { title: 'Digital Nagar Palika', subtitle: 'Municipal services, all in one place', hello: 'Namaskar!', actions: ['Raise a complaint', 'My complaints', 'Municipal services', 'News & notices', 'Emergency contacts', 'Schemes'], language: 'Language' },
};
type Locale = keyof typeof strings;
export default function Home() {
  const [locale, setLocale] = useState<Locale>('mr'); const t = strings[locale];
  return <SafeAreaView style={{ flex: 1, backgroundColor: '#f5f8f5' }}><ScrollView contentContainerStyle={{ padding: 22, gap: 18 }}>
    <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}><Text style={{ fontSize: 20, fontWeight: '700', color: '#0a493d' }}>{t.title}</Text><Pressable accessibilityRole="button" accessibilityLabel={t.language} onPress={() => setLocale(locale === 'mr' ? 'hi' : locale === 'hi' ? 'en' : 'mr')}><Text style={{ color: '#126b58' }}>मराठी · हिन्दी · EN</Text></Pressable></View>
    <Text style={{ color: '#60736f' }}>{t.subtitle}</Text><Text style={{ fontSize: 32, fontWeight: '600', color: '#183431' }}>{t.hello}</Text>
    {t.actions.map((action, i) => <Pressable key={action} accessibilityRole="button" onPress={() => {}} style={{ backgroundColor: 'white', borderRadius: 12, borderWidth: 1, borderColor: '#dce7df', padding: 18, minHeight: 58, justifyContent: 'center' }}><Text style={{ fontSize: 16, color: '#183431' }}>{['＋','◷','▤','▣','☎','✿'][i]}   {action}</Text></Pressable>)}
    <Text style={{ color: '#60736f', lineHeight: 22 }}>Emergency numbers and service information are shown only after the municipality verifies its official sources.</Text>
  </ScrollView></SafeAreaView>;
}
