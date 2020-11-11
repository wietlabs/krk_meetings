import * as React from "react";
import { Alert, View } from "react-native";
import { Button, TextInput } from "react-native-paper";
import { findConnections } from "../../api/ConnectionsApi";

export default function HomeScreen({ navigation }) {
  const [startStopName, setStartStopName] = React.useState("Czerwone Maki P+R");
  const [endStopName, setEndStopName] = React.useState("Jerzmanowskiego");
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
    <View style={{ padding: 16 }}>
      <TextInput
        value={startStopName}
        label="Przystanek początkowy"
        left={<TextInput.Icon name="map-marker" />}
        right={
          <TextInput.Icon name="close" onPress={() => setStartStopName("")} />
        }
        onChangeText={setStartStopName}
        style={{ backgroundColor: "white", marginBottom: 16 }}
      />
      <Button
        mode="outlined"
        compact={true}
        icon="autorenew"
        color="gray"
        onPress={handleSwap}
        style={{
          width: 50,
          marginBottom: 16,
          marginLeft: "auto",
          marginRight: "auto",
        }}
      ></Button>
      <TextInput
        value={endStopName}
        label="Przystanek końcowy"
        left={<TextInput.Icon name="map-marker" />}
        right={
          <TextInput.Icon name="close" onPress={() => setEndStopName("")} />
        }
        onChangeText={setEndStopName}
        style={{ backgroundColor: "white", marginBottom: 16 }}
      />
      <Button
        mode="contained"
        loading={loading}
        icon={loading ? null : "magnify"}
        onPress={handleSubmit}
      >
        Wyszukaj połączenie
      </Button>
    </View>
  );
}
