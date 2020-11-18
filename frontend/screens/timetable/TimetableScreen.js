import * as React from "react";
import { WebView } from "react-native-webview";

export default function TimetableScreen() {
  return (
    <WebView
      source={{ uri: "http://rozklady.ztp.krakow.pl/" }}
      originWhitelist={["http://rozklady.ztp.krakow.pl"]}
      style={{ backgroundColor: "white" }}
    />
  );
}
