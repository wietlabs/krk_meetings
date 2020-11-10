import * as React from "react";
import {
  Clipboard,
  RefreshControl,
  ScrollView,
  Share,
  ToastAndroid,
} from "react-native";
import { ActivityIndicator, Chip, List } from "react-native-paper";
import { getMeeting } from "../../Api";

export default function MeetingDetailsScreen({ navigation, route }) {
  const userUuid = route.params.userUuid;
  const meetingUuid = route.params.meetingUuid;

  const [meeting, setMeeting] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [refreshing, setRefreshing] = React.useState(false);

  const refresh = async () => {
    setRefreshing(true);
    const meeting = await getMeeting(meetingUuid);
    setMeeting(meeting);
    setLoading(false);
    setRefreshing(false);
  };

  React.useEffect(() => {
    refresh();
  }, []);

  React.useLayoutEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <Chip icon="account-circle" style={{ marginRight: 16 }} mode="outlined">
          {userUuid.slice(0, 8)}
        </Chip>
      ),
    });
  }, [navigation]);

  React.useLayoutEffect(() => {
    if (meeting) navigation.setOptions({ title: meeting.name });
  }, [meeting]);

  const meetingUrl = `krk-meetings://${meetingUuid}`;

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
    <ScrollView
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={refresh} />
      }
    >
      <List.Subheader>Członkowie ({meeting.members.length})</List.Subheader>
      {meeting.members.map((member, i) => (
        <List.Item
          key={i}
          title={member.nickname}
          // description={"Czerwone Maki P+R"}
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
  );
}
