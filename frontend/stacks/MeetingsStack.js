import * as React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import AccountsScreen from "../screens/accounts/AccountsScreen";
import AddAccountScreen from "../screens/accounts/AddAccountScreen";
import ShowAccountQRCodeScreen from "../screens/accounts/ShowAccountQRCodeScreen";
import ScanAccountQRCodeScreen from "../screens/accounts/ScanAccountQRCodeScreen";
import MeetingsScreen from "../screens/meetings/MeetingsScreen";
import MeetingDetailsScreen from "../screens/meetings/details/MeetingDetailsScreen";
import SelectStartStopScreen from "../screens/meetings/SelectStartStopScreen";
import SelectEndStopScreen from "../screens/meetings/SelectEndStopScreen";
import CreateMeetingScreen from "../screens/meetings/create/CreateMeetingScreen";
import JoinMeetingScreen from "../screens/meetings/join/JoinMeetingScreen";

const Stack = createStackNavigator();

export default function MeetingsStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="Accounts"
        component={AccountsScreen}
        options={{ title: "Wybierz tożsamość" }}
      />
      <Stack.Screen
        name="AddAccount"
        component={AddAccountScreen}
        options={{ title: "Dodaj tożsamość" }}
      />
      <Stack.Screen
        name="Meetings"
        component={MeetingsScreen}
        options={{ title: "Spotkania" }}
      />
      <Stack.Screen
        name="MeetingDetails"
        component={MeetingDetailsScreen}
        options={{ title: "Spotkanie" }}
      />
      <Stack.Screen
        name="SelectStartStop"
        component={SelectStartStopScreen}
        options={{ title: "Wybierz punkt początkowy" }}
      />
      <Stack.Screen
        name="SelectEndStop"
        component={SelectEndStopScreen}
        options={{ title: "Wybierz miejsce spotkania" }}
      />
      <Stack.Screen
        name="CreateMeeting"
        component={CreateMeetingScreen}
        options={{ title: "Utwórz nowe spotkanie" }}
      />
      <Stack.Screen
        name="JoinMeeting"
        component={JoinMeetingScreen}
        options={{ title: "Dołącz do spotkania" }}
      />
      <Stack.Screen
        name="ShowAccountQRCode"
        component={ShowAccountQRCodeScreen}
        options={{ title: "Kod QR" }}
      />
      <Stack.Screen
        name="ScanAccountQRCode"
        component={ScanAccountQRCodeScreen}
        options={{ title: "Skanuj kod QR" }}
      />
    </Stack.Navigator>
  );
}
