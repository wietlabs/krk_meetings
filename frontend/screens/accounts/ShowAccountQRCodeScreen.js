import * as React from "react";
import { View, Text } from "react-native";
import SvgQRCode from "react-native-qrcode-svg";

export default function ShowAccountQRCodeScreen({ route }) {
  const data = route.params.data;

  return (
    <View
      style={{
        flex: 1,
        padding: 24,
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "white",
      }}
    >
      <SvgQRCode value={data} size={300} />
      <Text style={{ textAlign: "center", marginTop: 20 }}>{data}</Text>
    </View>
  );
}
