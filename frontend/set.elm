import Html exposing (Html, button, div, text, input)
import Html.Events exposing (onClick, onInput)
import Html.Attributes exposing (placeholder)
import WebSocket exposing (listen, send)
import Json.Decode exposing (Decoder, field, map2, int, string, list, bool, maybe, decodeString)

serverAddress = "ws://localhost:8001"

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
  }

type alias ServerState =
  { players : List Player
  , game : Maybe Game
  }

type alias Player =
  { name : String
  , points : Int
  }

type alias Game =
  { board : Board
  , gameOver: Bool
  }

type alias Board = List (List Int)




serverStateDecoder : Decoder ServerState
serverStateDecoder =
  map2 ServerState
    (field "players" (list playerDecoder))
    (field "game" (maybe gameDecoder))

playerDecoder : Decoder Player
playerDecoder =
  map2 Player
    (field "name" string)
    (field "points" int)

gameDecoder : Decoder Game
gameDecoder =
  map2 Game
    (field "board" boardDecoder)
    (field "game_over" bool)

boardDecoder : Decoder Board
boardDecoder =
  (list (list int))



init : (Model, Cmd Msg)
init =
  (Model (ServerState [] Nothing) "" False, Cmd.none)



-- UPDATE


type Msg
  = UpdateName String
  | Join
  | ServerMessage String


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
          ({model | server = server}, Cmd.none)


subscriptions model =
  listen serverAddress ServerMessage


-- VIEW


view : Model -> Html Msg
view model =
  if model.joined then
    div [] [ text (toString model) ]
  else
    viewLogin model

viewLogin : Model -> Html Msg
viewLogin model =
  div []
    [ input [ placeholder "Your name", onInput UpdateName ] []
    , button [ onClick Join ] [ text "join" ]
    ]
