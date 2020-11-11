import * as React from "react";
import { Alert, Clipboard, ToastAndroid, View } from "react-native";
import { Button, TextInput } from "react-native-paper";
import { validateLink, validateUuid, censorUuid } from "../../utils";
import { getNickname } from "../../UserManager";
import { checkIfMeetingExists, joinMeeting } from "../../api/MeetingsApi";

export default function JoinMeetingScreen({ navigation, route }) {
  const userUuid = route.params.userUuid;
  const [meetingUuid, setMeetingUuid] = React.useState("");
  const [nickname, setNickname] = React.useState("");

  const meetingUuidRef = React.useRef();
  const nicknameRef = React.useRef();

  navigation.addListener("focus", async () => {
    let loaded = false;
    if (!meetingUuid) loaded = await loadFromClipboard();
    if (!loaded) meetingUuidRef.current.focus();
    suggestNickname();
  });

  const suggestNickname = async () => {
    if (!nickname) {
      const nickname = await getNickname(userUuid);
      setNickname(nickname);
    }
  };

  const loadFromClipboard = async () => {
    const string = await Clipboard.getString();
    const trimmed = string.trim();
    if (!validateLink(trimmed)) return false;
    const meetingUuid = trimmed.slice("krk-meetings://".length);
    setMeetingUuid(meetingUuid);
    ToastAndroid.show("Wczytano ze schowka", ToastAndroid.SHORT);
    return true;
  };

  const showError = (message, fieldRef) => {
    Alert.alert("Wystąpił błąd", message, [
      { text: "OK", onPress: () => fieldRef.current.focus() },
    ]);
  };

  const validate = () => {
    if (!nickname) {
      showError("Proszę wpisać pseudonim", nicknameRef);
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    const meetingExists = await checkIfMeetingExists(meetingUuid);
    if (!meetingExists) {
      Alert.alert(
        "Wystąpił błąd",
        `Nie znaleziono spotkania o podanym identyfikatorze.`
      );
      return;
    }

    try {
      await joinMeeting({ meetingUuid, userUuid, nickname });
    } catch (e) {
      const error = e.response.data["error"];
      if (error == "Already a member") {
        Alert.alert("", "Jesteś już członkiem tego spotkania");
      } else {
        Alert.alert("Wystąpił błąd", error);
        return;
      }
    }

    navigation.pop(2);
    navigation.push("Meetings", { userUuid: userUuid });
    navigation.navigate("MeetingDetails", {
      userUuid: userUuid,
      meetingUuid: meetingUuid,
    });
  };

  const meetingUuidValid = validateUuid(meetingUuid);
  const disabled = !meetingUuidValid;

  return (
    <View style={{ padding: 16 }}>
      <TextInput
        ref={meetingUuidRef}
        label="Identyfikator spotkania"
        value={meetingUuid}
        left={<TextInput.Icon name="key" />}
        disabled={true}
        onChangeText={(meetingUuid) => setMeetingUuid(meetingUuid)}
        style={{ marginBottom: 16 }}
      />
      <TextInput
        label="Identyfikator tożsamości"
        value={censorUuid(userUuid)}
        left={<TextInput.Icon name="account-key" />}
        disabled={true}
        style={{ marginBottom: 16 }}
      />
      <TextInput
        ref={nicknameRef}
        label="Pseudonim"
        value={nickname}
        left={<TextInput.Icon name="account-outline" />}
        onChangeText={(nickname) => setNickname(nickname)}
        style={{ backgroundColor: "white", marginBottom: 16 }}
      />
      <Button mode="contained" disabled={disabled} onPress={handleSubmit}>
        Dołącz
      </Button>
    </View>
  );
}
