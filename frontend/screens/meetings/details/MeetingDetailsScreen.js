import * as React from "react";
import {
  Alert,
  Clipboard,
  RefreshControl,
  ScrollView,
  Share,
  ToastAndroid,
} from "react-native";
import { ActivityIndicator, Button, Chip, List } from "react-native-paper";
import { getMeetingDetails } from "../../../api/MeetingsApi";
import { createMeetingLink } from "../../../LinkManager";
import { getNickname } from "../../../UserManager";

export default function MeetingDetailsScreen({ navigation, route }) {
  const userUuid = route.params.userUuid;
  const meetingUuid = route.params.meetingUuid;

  const [meeting, setMeeting] = React.useState(null);
  const [nickname, setNickname] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [refreshing, setRefreshing] = React.useState(false);

  const refresh = async () => {
    setRefreshing(true);
    await Promise.all([loadNickname(), loadMeeting()]);
    setLoading(false);
    setRefreshing(false);
  };

  const loadNickname = async () => {
    const nickname = await getNickname(userUuid);
    setNickname(nickname);
  };

  const loadMeeting = async () => {
    const meeting = await getMeetingDetails(meetingUuid, userUuid);
    setMeeting(meeting);
  };

  React.useEffect(() => {
    navigation.addListener("focus", () => {
      refresh();
    });
  }, []);

  React.useLayoutEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <Chip icon="account-circle" style={{ marginRight: 16 }} mode="outlined">
          {nickname || userUuid.slice(0, 8)}
        </Chip>
      ),
    });
  }, [navigation, nickname]);

  React.useLayoutEffect(() => {
    if (meeting) navigation.setOptions({ title: meeting.name });
  }, [meeting]);

  const startStopName = meeting?.membership?.stop_name;
  const endStopName = meeting?.stop_name;
  const isMeetingOwner = meeting?.membership?.is_owner;
  const meetingUrl = createMeetingLink(meetingUuid);

  const handleSelectStartStop = () => {
    navigation.navigate("SelectStartStop", { meetingUuid, userUuid });
  };

  const handleSelectEndStop = () => {
    if (!isMeetingOwner) {
      Alert.alert(
        "Wystąpił błąd",
        "Tylko organizator może ustawić miejsce spotkania."
      );
      return;
    }

    navigation.navigate("SelectEndStop", { meetingUuid, userUuid });
  };

  const handleFindConnections = () => {
    navigation.navigate("ConnectionsStack", {
      screen: "FindConnections",
      params: { startStopName, endStopName },
    });
  };

  const handleCopyToClipboard = () => {
    Clipboard.setString(meetingUrl);
    ToastAndroid.show("Skopiowano do schowka", ToastAndroid.SHORT);
  };

  const handleShare = () => {
    Share.share({ message: meetingUrl });
  };

  if (loading) {
    return (
      <ActivityIndicator
        size="large"
        animating={loading}
        style={{ marginTop: 32 }}
      />
    );
  }

  return (
    <>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={refresh} />
        }
      >
        <List.Subheader>Twoja lokalizacja</List.Subheader>
        <List.Item
          title={startStopName || "Wybierz punkt początkowy..."}
          left={(props) => (
            <List.Icon {...props} icon="map-marker" style={{ margin: 0 }} />
          )}
          onPress={handleSelectStartStop}
          style={{ backgroundColor: "white" }}
          titleStyle={
            startStopName
              ? { fontWeight: "bold" }
              : { color: "rgba(0, 0, 0, 0.5)" }
          }
        />
        <List.Subheader>Miejsce spotkania</List.Subheader>
        <List.Item
          title={
            endStopName ||
            (isMeetingOwner
              ? "Wybierz miejsce spotkania..."
              : "Nie wybrano miejsca spotkania")
          }
          left={(props) => (
            <List.Icon {...props} icon="flag-checkered" style={{ margin: 0 }} />
          )}
          onPress={handleSelectEndStop}
          style={{ backgroundColor: "white" }}
          titleStyle={
            endStopName
              ? { fontWeight: "bold" }
              : { color: "rgba(0, 0, 0, 0.5)" }
          }
        />
        <Button
          mode="contained"
          disabled={!startStopName || !endStopName}
          icon="magnify"
          style={{
            marginLeft: 16,
            marginRight: 16,
            marginTop: 8,
            marginBottom: 8,
          }}
          onPress={handleFindConnections}
        >
          Znajdź połączenie
        </Button>
        <List.Subheader>Członkowie ({meeting.members.length})</List.Subheader>
        {meeting.members.map((member, i) => (
          <List.Item
            key={i}
            title={member.nickname}
            description={member.stop_name}
            left={(props) => (
              <List.Icon {...props} icon="account" style={{ margin: 0 }} />
            )}
            right={
              member.is_owner
                ? (props) => (
                    <List.Icon
                      {...props}
                      icon="crown"
                      color="goldenrod"
                      style={{ margin: 0 }}
                    />
                  )
                : null
            }
            onPress={() => {}}
            style={{ backgroundColor: "white" }}
          />
        ))}
        <List.Subheader>Zaproś znajomych</List.Subheader>
        <List.Item
          title={meetingUrl}
          titleStyle={{
            color: "dodgerblue",
            textDecorationLine: "underline",
          }}
          left={(props) => (
            <List.Icon {...props} icon="link" style={{ margin: 0 }} />
          )}
          onPress={handleCopyToClipboard}
          onLongPress={() =>
            navigation.navigate("JoinMeeting", { meetingUuid })
          }
          style={{ backgroundColor: "white" }}
        />
        <List.Item
          title="Udostępnij..."
          left={(props) => (
            <List.Icon {...props} icon="share-variant" style={{ margin: 0 }} />
          )}
          onPress={handleShare}
          style={{ backgroundColor: "white" }}
        />
      </ScrollView>
    </>
  );
}
