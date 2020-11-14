import * as React from "react";
import { WebView } from "react-native-webview";

const url = "http://rozklady.mpk.krakow.pl/";

export default function TimetableScreen() {
  return <WebView source={{ uri: url }} style={{ marginTop: 25 }} />;
}
