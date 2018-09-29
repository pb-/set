module Main exposing (Board, Card, Game, Model, Msg(..), Player, ServerState, boardDecoder, decodeCard, gameDecoder, init, main, messageTypeDecoder, playerDecoder, serverAddress, serverStateDecoder, shapes, subscriptions, update, view, viewCard, viewControls, viewGame, viewLogin, viewPlayers, viewState)

import Html exposing (Html, button, div, input, table, td, text, tr)
import Html.Attributes exposing (class, placeholder, style)
import Html.Events exposing (onClick, onInput)
import Json.Decode exposing (Decoder, bool, decodeString, field, int, list, map2, map3, maybe, string)
import Json.Encode as JE
import Set
import Svg exposing (path, svg)
import Svg.Attributes exposing (d, viewBox)
import WebSocket exposing (listen, send)


serverAddress =
    "ws://10.0.0.8:8001"


shapes i =
    case i of
        0 ->
            "M50 10 l40 20 l-40 20 l-40 -20 Z"

        1 ->
            "M25 45 h50 a15 15 0 0 0 0 -30 h-50 a15 15 0 0 0 0 30"

        2 ->
            "M20 30 m-9.19 -9.19 a13 13 0 0 0 18.38 18.38 a8.21 8.21 0 0 1 11.62 0 a34.21 34.21 0 0 0 48.38 0 a13 13 0 0 0 -18.38 -18.38 a8.21 8.21 0 0 1 -11.62 0 a34.21 34.21 0 0 0 -48.38 0"

        _ ->
            ""


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
    , lastMsg : ServerMsg
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
    , gameOver : Bool
    , deckCount : Int
    }


type alias Card =
    { color : Int
    , shape : Int
    , count : Int
    , shading : Int
    }


type alias Board =
    List (List Int)


type alias SetConfirmed =
    { cards : List Int
    , player : String
    }


messageTypeDecoder : Decoder String
messageTypeDecoder =
    field "type" string


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
    list (list int)


setConfirmedDecoder : Decoder SetConfirmed
setConfirmedDecoder =
    map2 SetConfirmed
        (field "cards" (list int))
        (field "player" string)


init : ( Model, Cmd Msg )
init =
    ( Model (ServerState [] Nothing) "" False Set.empty NoMsg, Cmd.none )



-- UPDATE


type Msg
    = UpdateName String
    | Join
    | ServerMessage String
    | ToggleCard Int
    | RequestCards


type ServerMsg
    = NoMsg
    | CardsDenied
    | SetConf SetConfirmed


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        Join ->
            ( { model | joined = True }, send serverAddress (JE.encode 0 (JE.object [ ( "type", JE.string "player-joined" ), ( "name", JE.string model.name ) ])) )

        UpdateName name ->
            ( { model | name = name }, Cmd.none )

        ServerMessage encoded ->
            case decodeString messageTypeDecoder encoded of
                Err _ ->
                    ( model, Cmd.none )

                Ok msgType ->
                    case msgType of
                        "cards-denied" ->
                            ( { model | lastMsg = CardsDenied }, Cmd.none )

                        "set-confirmed" ->
                            case decodeString setConfirmedDecoder encoded of
                                Err _ ->
                                    ( model, Cmd.none )

                                Ok setConfirmed ->
                                    ( { model | lastMsg = SetConf setConfirmed }, Cmd.none )

                        "state" ->
                            case decodeString serverStateDecoder encoded of
                                Err _ ->
                                    ( model, Cmd.none )

                                Ok server ->
                                    let
                                        boardCards =
                                            case server.game of
                                                Just game ->
                                                    Set.fromList (List.concat game.board)

                                                Nothing ->
                                                    Set.empty
                                    in
                                    ( { model
                                        | server = server
                                        , selected = Set.intersect model.selected boardCards
                                      }
                                    , Cmd.none
                                    )

                        _ ->
                            ( model, Cmd.none )

        ToggleCard num ->
            let
                selected =
                    (if Set.member num model.selected then
                        Set.remove

                     else
                        Set.insert
                    )
                        num
                        model.selected

                cmd =
                    if Set.size selected == 3 then
                        send serverAddress (JE.encode 0 (JE.object [ ( "type", JE.string "set-announced" ), ( "cards", JE.list (List.map JE.int (Set.toList selected)) ) ]))

                    else
                        Cmd.none
            in
            ( { model
                | selected =
                    if Set.size selected == 3 then
                        Set.empty

                    else
                        selected
              }
            , cmd
            )

        RequestCards ->
            ( model, send serverAddress (JE.encode 0 (JE.object [ ( "type", JE.string "cards-wanted" ) ])) )


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
            [ viewState model ]

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
            div [] [ text "Waiting for another player" ]

        Just game ->
            case game.gameOver of
                True ->
                    div [] [ text "Game is over!" ]

                False ->
                    div []
                        [ div
                            [ style [ ( "grid-template-columns", "repeat(" ++ toString (List.length game.board) ++ ", 1fr)" ) ]
                            , class "board"
                            ]
                            (List.map (viewCard model) (List.concat game.board))
                        , div [] [ text (toString game.deckCount ++ " cards left in deck") ]
                        , div [ class "message" ]
                            [ case model.lastMsg of
                                NoMsg ->
                                    text ""

                                CardsDenied ->
                                    text "There is still a set!"

                                SetConf setConf ->
                                    div [] (text (setConf.player ++ " found a set: ") :: List.map (viewCard model) setConf.cards)
                            ]
                        ]


viewCard : Model -> Int -> Html Msg
viewCard model card =
    case card of
        (-1) ->
            div [ class "card empty" ] []

        _ ->
            let
                c =
                    decodeCard card

                selected =
                    if Set.member card model.selected then
                        " selected"

                    else
                        ""
            in
            div
                [ class ("card col" ++ toString c.color ++ " sh" ++ toString c.shading ++ selected)
                , onClick (ToggleCard card)
                ]
                (List.repeat (c.count + 1) (svg [ viewBox "-10 5 120 50" ] [ path [ d (shapes c.shape) ] [] ]))


viewControls : Model -> Html Msg
viewControls model =
    button [ onClick RequestCards ] [ text "No set" ]


viewPlayers : Model -> Html Msg
viewPlayers model =
    let
        viewPlayer player =
            tr []
                [ td [] [ text player.name ]
                , td []
                    [ text
                        (if player.wants_cards then
                            "wants cards"

                         else
                            ""
                        )
                    ]
                , td [] [ text (toString player.points) ]
                ]
    in
    table [] (List.map viewPlayer model.server.players)
