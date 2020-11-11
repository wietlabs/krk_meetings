import * as React from "react";
import { Alert, ToastAndroid, StyleSheet } from "react-native";
import { BarCodeScanner } from "expo-barcode-scanner";
import Placeholder from "../../components/Placeholder";
import { parseUserLink, validateUserLink } from "../../LinkManager";
import { addUser, hasUser } from "../../UserManager";
import { checkIfUserExists } from "../../api/MeetingsApi";

export default function ScanAccountQRCodeScreen({ navigation }) {
  const [hasPermission, setHasPermission] = React.useState(null);
  const [scanned, setScanned] = React.useState(false);

  const askForPermission = async () => {
    const { status } = await BarCodeScanner.requestPermissionsAsync();
    setHasPermission(status === "granted");
  };

  React.useEffect(() => {
    askForPermission();
  }, []);

  const handleBarCodeScanned = async ({ data }) => {
    setScanned(true);

    if (!validateUserLink(data)) {
      Alert.alert(
        "Wystąpił błąd",
        "Zeskanowany kod QR nie zawiera prawidłowego identyfikatora tożsamości.",
        [{ text: "OK", onPress: () => setScanned(false) }]
      );
      return;
    }

    const userUuid = parseUserLink(data);

    const alreadyAdded = await hasUser(userUuid);
    if (alreadyAdded) {
      Alert.alert("Wystąpił błąd", `Tożsamość ${userUuid} została już dodana.`);
      navigation.pop();
      return;
    }

    const userExists = checkIfUserExists(userUuid);
    if (!userExists) {
      Alert.alert(
        "Wystąpił błąd",
        `Nie znaleziono tożsamości o podanym identyfikatorze.`
      );
      navigation.pop();
      return;
    }

    await addUser({ uuid: userUuid, nickname: null });
    ToastAndroid.show("Tożsamość została dodana!", ToastAndroid.SHORT);
    navigation.pop();
    navigation.replace("Accounts");
  };

  if (hasPermission === null) {
    return <Placeholder icon="camera-off" text="Oczekiwanie na uprawnienia" />;
  }

  if (hasPermission === false) {
    return <Placeholder icon="camera-off" text="Brak dostępu do kamery" />;
  }

  return (
    <BarCodeScanner
      barCodeTypes={[BarCodeScanner.Constants.BarCodeType.qr]}
      onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
      style={{ ...StyleSheet.absoluteFillObject, backgroundColor: "black" }}
    />
  );
}
