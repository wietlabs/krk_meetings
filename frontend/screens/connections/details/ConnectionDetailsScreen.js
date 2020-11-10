import * as React from "react";
import { View } from "react-native";
import { Divider } from "react-native-paper";
import Map from "./map/Map";
import ActionsList from "./actions/ActionsList";

export default function ConnectionDetailsScreen({ route }) {
  const connection = route.params.connection;

  return (
    <View>
      <Map connection={connection} />
      <Divider />
      <ActionsList connection={connection} />
    </View>
  );
}
