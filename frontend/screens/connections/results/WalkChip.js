import * as React from "react";
import { Chip } from "react-native-paper";

export default function WalkButton({ duration }) {
  return (
    <Chip icon="walk" color="whitesmoke" style={{ marginRight: 6 }}>
      {duration} min
    </Chip>
  );
}
