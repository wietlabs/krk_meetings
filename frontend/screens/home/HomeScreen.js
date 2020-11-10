import * as React from "react";
import { Alert, View } from "react-native";
import { Button, Searchbar } from "react-native-paper";
import { findConnections } from "../../api/ConnectionsApi";

export default function HomeScreen({ navigation }) {
  const [startStopName, setStartStopName] = React.useState("Czerwone Maki P+R");
  const [endStopName, setEndStopName] = React.useState("Łagiewniki");
  const [loading, setLoading] = React.useState(false);

  const handleSwap = () => {
    setStartStopName(endStopName);
    setEndStopName(startStopName);
  };

  const handleSubmit = async () => {
    setLoading(true);
    const startDateTime = new Date(2020, 11, 10, 16, 0, 0); // TODO: handle input
    const query = { startDateTime, startStopName, endStopName };
    try {
      const connections = await findConnections(query);
      navigation.navigate("ConnectionResults", { connections });
    } catch (e) {
      Alert.alert(
        "Wystąpił błąd",
        "Wystąpił błąd podczas wyszukiwania połączenia."
      );
    }
    setLoading(false);
  };

  return (
    <View style={{ alignItems: "center", padding: 20, paddingTop: 80 }}>
      <Searchbar
        placeholder="Przystanek początkowy"
        value={startStopName}
        icon="adjust"
        style={{ marginBottom: 16 }}
        onChangeText={(text) => setStartStopName(text)}
      />
      <Button
        mode="outlined"
        compact={true}
        icon="autorenew"
        style={{ marginBottom: 16 }}
        color="gray"
        onPress={handleSwap}
      ></Button>
      <Searchbar
        placeholder="Przystanek końcowy"
        value={endStopName}
        icon="map-marker"
        style={{ marginBottom: 80 }}
        onChangeText={(text) => setEndStopName(text)}
      />
      <Button
        mode="contained"
        loading={loading}
        icon={loading ? null : "magnify"}
        style={{ width: 250 }}
        onPress={handleSubmit}
      >
        Wyszukaj połączenie
      </Button>
    </View>
  );
}
