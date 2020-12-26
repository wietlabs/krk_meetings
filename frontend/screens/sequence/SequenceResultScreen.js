import * as React from "react";
import { ScrollView, View } from "react-native";
import { List, Button } from "react-native-paper";

export default function SequenceResultScreen({ navigation, route }) {
  const sequence = route.params.sequence;

  const getNthIcon = (n) => {
    if (n == 0) return "flag-outline";
    if (n == sequence.length - 1) return "flag-checkered";
    return "map-marker-outline";
  };

  const findNthConnection = async (n) => {
    const [startStopName, endStopName] = sequence.slice(n);
    navigation.navigate("ConnectionsStack", {
      screen: "FindConnections",
      params: { startStopName, endStopName },
    });
  };

  return (
    <ScrollView>
      <View style={{ paddingVertical: 8, paddingHorizontal: 16 }}>
        {sequence.map((stop, n) => (
          <React.Fragment key={n}>
            <List.Item
              title={stop}
              titleStyle={{
                fontWeight:
                  n == 0 || n == sequence.length - 1 ? "bold" : "normal",
              }}
              left={(props) => (
                <List.Icon
                  {...props}
                  icon={getNthIcon(n)}
                  style={{ margin: 0 }}
                />
              )}
              style={{ paddingHorizontal: 0 }}
            />
            {n < sequence.length - 1 && (
              <Button
                mode="contained"
                color="khaki"
                icon="arrow-down"
                onPress={() => findNthConnection(n)}
              >
                Wyszukaj połączenia
              </Button>
            )}
          </React.Fragment>
        ))}
      </View>
    </ScrollView>
  );
}
