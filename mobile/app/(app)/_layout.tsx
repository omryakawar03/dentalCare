import { Tabs } from "expo-router";

export default function AppTabs() {
  return <Tabs screenOptions={{headerShown:false, tabBarActiveTintColor:"#087f78", tabBarInactiveTintColor:"#71818b", tabBarLabelStyle:{fontSize:10}, tabBarStyle:{height:62,paddingTop:7,paddingBottom:8}}}>
    <Tabs.Screen name="home" options={{title:"Home",tabBarIcon:()=>null}}/>
    <Tabs.Screen name="schedule" options={{title:"Schedule",tabBarIcon:()=>null}}/>
    <Tabs.Screen name="patients" options={{title:"Patients",tabBarIcon:()=>null}}/>
    <Tabs.Screen name="more" options={{title:"More",tabBarIcon:()=>null}}/>
  </Tabs>;
}
