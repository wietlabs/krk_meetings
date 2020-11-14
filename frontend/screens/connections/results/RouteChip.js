import * as React from "react";
import { Chip } from "react-native-paper";

export default function RouteButton({ routeName, nth }) {
  const colors = ["deepskyblue", "chartreuse", "gold", "salmon"];
  const color = colors[Math.min(nth, colors.length - 1)];

  const isBus = routeName.length == 3;
  const icon = isBus ? "bus" : "tram";

  return (
    <Chip icon={icon} style={{ marginRight: 6, backgroundColor: color }}>
      {routeName}
    </Chip>
  );
}
