import { Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
export default function MoreScreen() { return <SafeAreaView className="flex-1 bg-clinic-canvas px-5"><Text className="mb-2 mt-6 text-2xl font-bold text-clinic-ink">More</Text>{["Inventory & barcode scan","Inbox","Reports","Team & access","Settings"].map(item=><View key={item} className="mt-2 rounded-xl border border-slate-100 bg-white p-4"><Text className="text-sm font-medium text-clinic-ink">{item}</Text></View>)}</SafeAreaView>; }
