import * as React from "react";
import { Text, View } from "react-native";
import { IconButton } from "react-native-paper";

export default function Placeholder({ icon, text }) {
  return (
    <View
      style={{
        position: "absolute",
        top: 0,
        bottom: 0,
        left: 0,
        right: 0,
        flex: 1,
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <IconButton icon={icon} size={100} color="lightgray" />
      <Text
        style={{
          fontSize: 24,
          color: "lightgray",
          textAlign: "center",
          paddingBottom: 50,
        }}
      >
        {text}
      </Text>
    </View>
  );
}
