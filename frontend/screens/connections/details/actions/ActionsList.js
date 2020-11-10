import * as React from "react";
import { ScrollView } from "react-native";
import Action from "./Action";

export default function ActionsList({ connection }) {
  const actions = connection.transfers; // TODO: rename to connection.actions

  return (
    <ScrollView style={{ height: "60%", padding: 16 }}>
      {actions.map((action, i) => (
        <Action action={action} key={i} />
      ))}
    </ScrollView>
  );
}
