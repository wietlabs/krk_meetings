import * as React from "react";
import { Text } from "react-native";

export default function DelayText({
  delay,
  style,
  delayedColor = "tomato",
  onTimeColor = "lightgray",
}) {
  if (delay === null) return null;

  const delayInMinutes = Math.round(delay / 60);
  const color = delayInMinutes > 0 ? delayedColor : onTimeColor;
  const text =
    delayInMinutes == 0
      ? "OK"
      : (delayInMinutes > 0 ? "+" : "") + delayInMinutes;

  return (
    <Text style={{ fontSize: 9, fontWeight: "bold", color, ...style }}>
      {text}
    </Text>
  );
}
