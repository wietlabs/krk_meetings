import * as React from "react";
import { Text, View } from "react-native";
import { IconButton } from "react-native-paper";

export default function GridLine({
  orientation,
  position,
  color = "lightgray",
  width = 1,
  icon,
  iconSize = 20,
  label,
}) {
  const style =
    orientation === "vertical"
      ? {
          left: position,
          top: 0,
          bottom: 0,
          borderLeftColor: color,
          borderLeftWidth: width,
        }
      : {
          top: position,
          left: 0,
          right: 0,
          borderTopColor: color,
          borderTopWidth: width,
        };

  return (
    <View
      style={{
        position: "absolute",
        ...style,
      }}
    >
      {icon && (
        <IconButton
          icon={icon}
          size={iconSize}
          color={color}
          style={{ marginTop: 3, marginLeft: 2, marginBottom: -8 }}
        />
      )}
      {label && (
        <Text style={{ color: color, marginLeft: 6, marginTop: 6 }}>
          {label}
        </Text>
      )}
    </View>
  );
}
