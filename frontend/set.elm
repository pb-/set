import Html exposing (Html, button, div, text, input, tr, td, table)
import Html.Events exposing (onClick, onInput)
import Html.Attributes exposing (placeholder, style, class)
import Svg exposing (path, svg)
import Svg.Attributes exposing (viewBox, d)
import WebSocket exposing (listen, send)
import Json.Decode exposing (Decoder, field, map2, map3, int, string, list, bool, maybe, decodeString)
import Json.Encode as JE
import Set

serverAddress = "ws://10.0.0.8:8001"

shapes i =
  case i of
    0 -> "M50 10 l40 20 l-40 20 l-40 -20 Z"
    1 -> "M25 45 h50 a15 15 0 0 0 0 -30 h-50 a15 15 0 0 0 0 30"
    2 -> "M20 30 m-9.19 -9.19 a13 13 0 0 0 18.38 18.38 a8.21 8.21 0 0 1 11.62 0 a34.21 34.21 0 0 0 48.38 0 a13 13 0 0 0 -18.38 -18.38 a8.21 8.21 0 0 1 -11.62 0 a34.21 34.21 0 0 0 -48.38 0"
    _ -> ""

main =
  Html.program
    { init = init
    , view = view
    , update = update
    , subscriptions = subscriptions
    }



-- MODEL


type alias Model =
  { server : ServerState
  , name : String
  , joined : Bool
  , selected : Set.Set Int
  }

type alias ServerState =
  { players : List Player
  , game : Maybe Game
  }

type alias Player =
  { name : String
  , points : Int
  , wants_cards : Bool
  }

type alias Game =
  { board : Board
  , gameOver: Bool
  , deckCount: Int
  }

type alias Card =
  { color : Int
  , shape : Int
  , count : Int
  , shading : Int
  }

type alias Board = List (List Int)




serverStateDecoder : Decoder ServerState
serverStateDecoder =
  map2 ServerState
    (field "players" (list playerDecoder))
    (field "game" (maybe gameDecoder))

playerDecoder : Decoder Player
playerDecoder =
  map3 Player
    (field "name" string)
    (field "points" int)
    (field "wants_cards" bool)

gameDecoder : Decoder Game
gameDecoder =
  map3 Game
    (field "board" boardDecoder)
    (field "game_over" bool)
    (field "deck_count" int)

boardDecoder : Decoder Board
boardDecoder =
  (list (list int))



init : (Model, Cmd Msg)
init =
  (Model (ServerState [] Nothing) "" False Set.empty, Cmd.none)



-- UPDATE


type Msg
  = UpdateName String
  | Join
  | ServerMessage String
  | ToggleCard Int
  | RequestCards


update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  case msg of
    Join ->
      ({model | joined = True}, send serverAddress ("{\"type\":\"player-joined\",\"name\":\"" ++ model.name ++ "\"}"))

    UpdateName name ->
      ({model | name = name}, Cmd.none)

    ServerMessage encoded ->
      case decodeString serverStateDecoder encoded of
        Err _ ->
          (model, Cmd.none)
        Ok server ->
          let
            boardCards =
              case server.game of
                Just game ->
                  Set.fromList (List.concat game.board)
                Nothing ->
                  Set.empty

          in
          ({ model
           | server = server
           , selected = Set.intersect model.selected boardCards}, Cmd.none)

    ToggleCard num ->
      let
        selected = (if Set.member num model.selected then Set.remove else Set.insert) num model.selected

        cmd = if Set.size selected == 3 then send serverAddress (JE.encode 0 (JE.object [("type", JE.string "set-announced"), ("cards", JE.list (List.map JE.int (Set.toList selected)))])) else Cmd.none
      in
      ({model | selected = if Set.size selected == 3 then Set.empty else selected}, cmd)

    RequestCards ->
      (model, send serverAddress (JE.encode 0 (JE.object [("type", JE.string "cards-wanted")])))


subscriptions model =
  listen serverAddress ServerMessage


-- VIEW

decodeCard : Int -> Card
decodeCard card =
  { color = card % 3
  , shape = card // 3 % 3
  , count = card // 9 % 3
  , shading = card // 27 % 3
  }


view : Model -> Html Msg
view model =
  if model.joined then
    div []
      [viewState model]
  else
    viewLogin model

viewLogin : Model -> Html Msg
viewLogin model =
  div []
    [ input [ placeholder "Your name", onInput UpdateName ] []
    , button [ onClick Join ] [ text "join" ]
    ]

viewState : Model -> Html Msg
viewState model =
  div []
    [ viewGame model
    , viewControls model
    , viewPlayers model
    ]

viewGame : Model -> Html Msg
viewGame model =
  case model.server.game of
    Nothing ->
      div [] [text "Waiting for another player"]
    Just game ->
      case game.gameOver of
        True ->
          div [] [text "Game is over!"]
        False ->
          div []
            [ div
                [ style [("grid-template-columns", "repeat(" ++ (toString (List.length game.board)) ++ ", 1fr)")]
                , class "board"
                ]
                (List.map (viewCard model) (List.concat game.board))
            , div [] [text ((toString game.deckCount) ++ " cards left in deck")]
            ]

viewCard : Model -> Int -> Html Msg
viewCard model card =
  case card of
    -1 -> div [class ("card empty")] []
    _ ->
      let
        c = decodeCard card
        selected = if Set.member card model.selected then " selected" else ""
      in
      div
        [ class ("card col" ++ (toString c.color) ++ " sh" ++ (toString c.shading) ++ selected)
        , onClick (ToggleCard card)
        ]
        (List.repeat (c.count + 1) (svg [viewBox "-10 5 120 50"] [path [d (shapes c.shape)] []]))

viewControls : Model -> Html Msg
viewControls model =
  button [onClick RequestCards] [text "No set"]

viewPlayers : Model -> Html Msg
viewPlayers model =
  let
    viewPlayer player =
      tr []
        [ td [] [ text player.name ]
        , td [] [ text (if player.wants_cards then "wants cards" else "") ]
        , td [] [ text (toString player.points) ]
        ]
  in
  table [] (List.map viewPlayer model.server.players)
