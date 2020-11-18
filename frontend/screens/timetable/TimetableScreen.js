import * as React from "react";
import { SafeAreaView, StatusBar } from "react-native";
import { WebView } from "react-native-webview";

const url = "http://rozklady.ztp.krakow.pl/";

export default function TimetableScreen() {
  return (
    <SafeAreaView
      style={{
        flex: 1,
        backgroundColor: "white",
        paddingTop: Platform.OS === "android" ? StatusBar.currentHeight : 0,
      }}
    >
      <WebView source={{ uri: url }} style={{ backgroundColor: "white" }} />
    </SafeAreaView>
  );
}
