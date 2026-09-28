import { ScrollView, Text, View, Pressable } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

const cards = [["Appointments", "—"], ["Collections", "—"], ["Pending", "—"], ["Follow-ups", "—"]];

export default function HomeScreen() {
  return <SafeAreaView className="flex-1 bg-clinic-canvas"><ScrollView className="flex-1 px-5" contentContainerStyle={{paddingBottom:28}}>
    <View className="mb-5 mt-3 flex-row items-center justify-between"><View><Text className="text-xs font-semibold uppercase tracking-widest text-clinic-teal">Clinic overview</Text><Text className="mt-2 text-2xl font-bold text-clinic-ink">Good morning</Text></View><Pressable accessibilityLabel="Choose clinic" className="rounded-lg border border-slate-200 bg-white px-3 py-2"><Text className="text-xs text-slate-700">All clinics⌄</Text></Pressable></View>
    <Text className="mb-4 text-sm text-slate-500">Your practice at a glance</Text>
    <View className="flex-row flex-wrap justify-between">{cards.map(([name,value])=><View key={name} className="mb-3 w-[48%] rounded-xl border border-slate-100 bg-white p-4"><Text className="text-xs text-slate-500">{name}</Text><Text className="mt-3 text-2xl font-bold text-clinic-ink">{value}</Text></View>)}</View>
    <View className="mt-1 rounded-xl border border-slate-100 bg-white p-4"><Text className="text-sm font-bold text-clinic-ink">Quick actions</Text><View className="mt-3 flex-row flex-wrap gap-2"><Quick label="＋ Patient"/><Quick label="▦ Appointment"/><Quick label="₹ Payment"/><Quick label="▤ Scan stock"/></View></View>
    <View className="mt-3 rounded-xl border border-slate-100 bg-white p-4"><Text className="text-sm font-bold text-clinic-ink">Needs attention</Text><Text className="mt-3 text-sm text-slate-500">Follow-ups, low stock and expiry alerts will appear here.</Text></View>
  </ScrollView></SafeAreaView>;
}
function Quick({label}:{label:string}) { return <Pressable className="rounded-lg bg-[#e7f5f2] px-3 py-3"><Text className="text-xs font-semibold text-clinic-teal">{label}</Text></Pressable>; }
