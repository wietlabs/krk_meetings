import * as React from "react";
import { ScrollView } from "react-native";
import ConnectionResult from "./ConnectionResult";

export default function ConnectionResults({ connections, navigation }) {
  return (
    <ScrollView style={{ padding: 16 }}>
      {connections.map((connection, i) => (
        <ConnectionResult
          connection={connection}
          navigation={navigation}
          key={i}
        />
      ))}
    </ScrollView>
  );
}
