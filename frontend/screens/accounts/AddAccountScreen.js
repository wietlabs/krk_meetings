import * as React from "react";
import { Alert, Clipboard, ToastAndroid, View } from "react-native";
import { Button, TextInput } from "react-native-paper";
import { validateUuid } from "../../utils";
import { addUser, hasUser } from "../../UserManager";
import { checkIfUserExists } from "../../api/MeetingsApi";

export default function AddAccountScreen({ navigation }) {
  const [uuid, setUuid] = React.useState("");

  const uuidRef = React.useRef();

  navigation.addListener("focus", async () => {
    let loaded = false;
    if (!uuid) loaded = await loadFromClipboard();
    if (!loaded) uuidRef.current.focus();
  });

  const loadFromClipboard = async () => {
    const string = await Clipboard.getString();
    const trimmed = string.trim();
    if (!validateUuid(trimmed)) return false;
    setUuid(trimmed);
    ToastAndroid.show("Wczytano ze schowka", ToastAndroid.SHORT);
    return true;
  };

  const handleSubmit = async () => {
    const alreadyAdded = await hasUser(uuid);
    if (alreadyAdded) {
      Alert.alert("Wystąpił błąd", `Tożsamość ${uuid} została już dodana.`);
      navigation.pop();
      return;
    }

    const userExists = await checkIfUserExists(uuid);
    if (!userExists) {
      Alert.alert(
        "Wystąpił błąd",
        `Nie znaleziono tożsamości o podanym identyfikatorze.`
      );
      return;
    }

    await addUser({ uuid, nickname: null });
    navigation.replace("Accounts");
  };

  const uuidValid = validateUuid(uuid);
  const disabled = !uuidValid;

  return (
    <View style={{ padding: 16 }}>
      <TextInput
        ref={uuidRef}
        label="Identyfikator tożsamości"
        value={uuid}
        left={<TextInput.Icon name="account-key" />}
        onChangeText={(uuid) => setUuid(uuid)}
        style={{ backgroundColor: "white", marginBottom: 16 }}
      />
      <Button mode="contained" disabled={disabled} onPress={handleSubmit}>
        Dodaj
      </Button>
    </View>
  );
}
