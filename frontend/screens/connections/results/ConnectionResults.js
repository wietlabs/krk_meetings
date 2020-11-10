import * as React from "react";
import { ScrollView } from "react-native";
import { IconButton } from "react-native-paper";
import ConnectionResult from "./ConnectionResult";

export default function ConnectionResults({ connections, navigation }) {
  const handleShowPlot = () => {
    navigation.navigate("ConnectionResultsPlot", { connections });
  };

  React.useLayoutEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <IconButton
          icon="chart-bar"
          onPress={handleShowPlot}
          style={{ marginRight: 16 }}
        />
      ),
    });
  }, [navigation]);

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
