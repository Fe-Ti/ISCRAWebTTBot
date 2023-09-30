# Copyright 2023 Fe-Ti aka T.Kravchenko
from redminebotlib.constants import *

scenery_source = {
    Start_state   : "start",
    Hint_template : "\n\n>>{}",
    States   :{
        "init1":{ # dummy
                Type    : Say,
                Error   : None,
                Info    : None,
                Phrase  : """""",
                Next    : "init2",
        },
        "init2":{
                Type    : Say,
                Error   : None,
                Info    : None,
                Phrase  : """А пока, как сказано в Слове, "Почнёмъ же, братие, повѣсть сию".""",
                Next    : "set_key",
                Properties : [Say_anyway, Lexeme_preserving]
        },
        "reset_user":{
            Type    : Say,
            Next    : "start",
            Functions: ["reset_user"],
            Properties : [Lexeme_preserving]
        },
        "start" : {
            Type    : Ask,
            Phrase  : "Введи команду.",
            Next    : {
                        "create"    : ["создай"],
                        "update"    : ["обнови","измени"],
                        "show"      : ["покажи"],
                        "delete"    : ["удали"],
                        "settings"  : ["запомни", "настрой"]
                    },
        },

        "delete" : {
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """Что ты хочешь удалить?""",
            Next    : {
                            "delete_project_get_id":["проект"],
                            "delete_issue_get_id":["задачу"],
                        },
            # ~ Properties : []
        },
        "delete_project_get_id" : {
            Type    : Get,
            Info    : "no_help",
            Phrase  : """Какой проект ты хочешь удалить?""",
            Next    : "approve_deletion",
            Input   : {Parameters:'id'},
            Set     : { Storage : { Context : Project }, },
            Functions: ["show"],
        },
        "delete_issue_get_id" : {
            Type    : Get,
            Info    : "no_help",
            Phrase  : """Какую задачу ты хочешь удалить?""",
            Next    : "approve_deletion",
            Input   : {Parameters:'id'},
            Set     : { Storage  : { Context : Issue } },
            Functions: ["show"],
        },
        "approve_deletion" : {
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """Ты точно хочешь удалить?""",
            Next    : {
                            "delete_call":["да"],
                            "reset_user":["нет"],
                        },
        },
        "delete_call" : {
            Type     : Say,
            Error    : "В ходе удаления произошла ошибка.",
            Info     : "no_help",
            Phrase   : """Удаляю объект...""",
            Next     : "reset_user",
            Functions: ["delete"],
            Properties : [Lexeme_preserving]
        },
        "create" : {
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """Какой тип объекта ты хочешь создать?""",
            Next    : {
                            "create_project_init_vars":["проект"],
                            "create_issue_init_vars":["задачу", "подзадачу"],
                        },
            # ~ Properties : []
        },
        "create_project_init_vars" : {
            Type    : Say,
            Error   : None,
            Info    : None,
            Phrase  : """Инициализирую переменные...""",
            Next    : "create_project_set_identifier",
            Set     :   {
                            Storage  : { Context : Project },
                            Data     : {
                                "name"          : "",
                                "identifier"    : "",
                                "description"   : ""
                            }
                        },
            Properties : [Lexeme_preserving]
        },
        "create_project_menu" : {
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """Что ты хочешь задать в проекте?""",
            Next    : {
                            "create_project_set_name":["название","имя"],
                            "create_project_set_identifier":["идентификатор", "id"],
                            "create_project_set_description":["описание"],
                            "create_call":["готово", ".", "!"]
                        },
        },
        "draft_show_project" : {
            Type    : Say,
            Phrase  : """Черновик проекта""",
            Next    : "create_project_menu",
            Functions: ["show_project_draft"],
            Properties : [Lexeme_preserving]
        },
        "create_project_set_identifier" : {
            Type    : Get,
            Phrase  : """Введи идентификатор проекта.""",
            Next    : "draft_show_project",
            Input   : {Data:'identifier'},
        },
        "create_project_set_name" : {
            Type    : Get,
            Phrase  : """Введи название проекта.""",
            Next    : "draft_show_project",
            Input   : {Data:'name'},
        },
        "create_project_set_description" : {
            Type    : Get,
            Phrase  : """Введи описание проекта.""",
            Next    : "draft_show_project",
            Input   : {Data:'description'},
        },
        "create_issue_init_vars" : {
            Type    : Ask,
            Info    : "no_help",
            Phrase  : """Инициализирую переменные... Продолжай """,
            Next    :   {
                        "create_issue_in_prep" : ["в"],
                        "create_issue_set_project_id" : ["проект"],
                        "create_issue_set_subject" : ["тема"]
                        },
            Set     :   {
                            Storage  : { Context : Issue },
                            Data     : {
                                "project_id"    : "",
                                "subject"       : "",
                                "description"   : "",
                                "start_date" : "",
                                "due_date" : "",
                                "status_id" : "",
                                "assigned_to_id" : "",
                                "tracker_id" : "",
                                "priority_id" : "",
                                "parent_issue_id" : "",
                                # ~ "" : "",
                            }
                        },
            Properties : [Lexeme_preserving]
        },
        "create_issue_in_prep":{
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """В чём?""",
            Next    :   {
                            "create_issue_set_project_id": ["проекте"],
                            "create_issue_set_parent_id": ["задаче"]
                        },
        },
        "create_issue_menu" : {
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """Что ты хочешь поменять в задаче?""",
            Next    : {
                            "create_issue_set_project_id" : ["проект"],
                            "create_issue_set_parent_id" : ["родителя","родитель"],
                            "create_issue_set_subject":["тему","тема"],
                            "create_issue_set_description":["описание"],
                            "create_issue_set_date":["дату","дата", "срок"],
                            "create_issue_set_assign0":["исполнителя","исполнитель", "назначена"],
                            "create_issue_set_tracker0":["трекер"],
                            "create_issue_set_priority0":["приоритет"],
                            "create_issue_set_status0":["статус"],
                            "create_call":["готово", "."]
                        },
        },
        "create_issue_set_assign0" : {
            Type    : Say,
            Next    : "create_issue_set_assign",
            Functions:["show_project_memberships"],
            Properties: [Lexeme_preserving]
        },
        "create_issue_set_tracker0" : {
            Type    : Say,
            Next    : "create_issue_set_tracker",
            Functions:["show_issue_trackers"],
            Properties: [Lexeme_preserving]
        },
        "create_issue_set_status0" : {
            Type    : Say,
            Next    : "create_issue_set_status",
            Functions:["show_issue_statuses"],
            Properties: [Lexeme_preserving]
        },
        "create_issue_set_priority0" : {
            Type    : Say,
            Next    : "create_issue_set_priority",
            Functions:["show_issue_priorities"],
            Properties: [Lexeme_preserving]
        },
        "draft_show_issue" : {
            Type    : Say,
            Phrase  : """Черновик задачи""",
            Next    : "create_issue_menu",
            Functions: ["show_issue_draft"],
            Properties : [Lexeme_preserving]
        },
        "create_issue_set_date":{
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """В чём?""",
            Next    :   {
                            "create_issue_set_date_start": ["начала"],
                            "create_issue_set_date_due" : ["завершения"]
                        },
        },
        "create_issue_set_project_id" : {
            Type    : Get,
            Phrase  : """Введи идентификатор проекта.""",
            Next    : "draft_show_issue",
            Input   : {Data:'project_id'},
        },
        "create_issue_set_parent_id" : {
            Type    : Get,
            Phrase  : """Введи идентификатор родительской задачи.""",
            Next    : "draft_show_issue",
            Input   : {Data:'parent_issue_id'},
            Functions: [["get_parent_issue_project_id","""not user.variables[Data]['project_id']"""],],
        },
        "create_issue_set_subject" : {
            Type    : Get,
            Phrase  : """Введи тему.""",
            Next    : "draft_show_issue",
            Input   : {Data:'subject'},
        },
        "create_issue_set_description" : {
            Type    : Get,
            Phrase  : """Введи описание.""",
            Next    : "draft_show_issue",
            Input   : {Data:'description'},
        },
        "create_issue_set_date_start" : {
            Type    : Get,
            Phrase  : """Введи дату начала. Например, 2023-08-02""",
            Next    : "draft_show_issue",
            Input   : {Data:'start_date'},
        },
        "create_issue_set_date_due" : {
            Type    : Get,
            Phrase  : """Введи срок завершения. Например, 2023-08-02""",
            Next    : "draft_show_issue",
            Input   : {Data:'due_date'},
        },
        "create_issue_set_assign" : {
            Type    : Get,
            Phrase  : """Введи ID пользователя, которому хочешь назначить задачу.""",
            Next    : "draft_show_issue",
            Input   : {Data:'assigned_to_id'},
        },
        "create_issue_set_tracker" : {
            Type    : Get,
            Phrase  : """Введи ID трекера.""",
            Next    : "draft_show_issue",
            Input   : {Data:'tracker_id'},
        },
        "create_issue_set_status" : {
            Type    : Get,
            Phrase  : """Введи ID статуса.""",
            Next    : "draft_show_issue",
            Input   : {Data:'status_id'},
        },
        "create_issue_set_priority" : {
            Type    : Get,
            Phrase  : """Введи ID приоритета.""",
            Next    : "draft_show_issue",
            Input   : {Data:'priority_id'},
        },
        "create_call" : {
            Type     : Say,
            Error    : "Мне не удалось создать объект.",
            Info     : "start",
            Phrase   : """Объект создан:""",
            Next     : "reset_user",
            Functions: ["create"],
            Properties : [Lexeme_preserving]
        },

        "update" : {
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """Какой тип объекта ты хочешь изменить?""",
            Next    : {
                            "update_project_get_id":["проект"],
                            "update_issue_get_id":["задачу"],
                        },
        },
        "update_project_get_id" : {
            Type    : Get,
            Error   : "data_get_error",
            Phrase  : """Какой проект? Введи идентификатор или номер.""",
            Next    : "update_draft_show_project",
            Set     :   {
                            Storage  : { Context : Project },
                        },
            Input   : {Parameters: "id"},
            Functions   : ["show", ["reset_to_start","""not user.variables[Storage][Success]"""]],
        },
        "update_project_menu" : {
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """Что ты хочешь задать в проекте?""",
            Next    : {
                            "update_project_set_name":["название","имя"],
                            "update_project_set_identifier":["идентификатор", "id"],
                            "update_project_set_description":["описание"],
                            "update_call":["готово", ".", "!"]
                        },
        },
        "update_draft_show_project" : {
            Type    : Say,
            Next    : "update_project_menu",
            Functions: ["show_project_update_draft"],
            Properties : [Lexeme_preserving]
        },
        "update_project_set_identifier" : {
            Type    : Get,
            Phrase  : """Введи идентификатор проекта.""",
            Next    : "update_draft_show_project",
            Input   : {Data:'identifier'},
        },
        "update_project_set_name" : {
            Type    : Get,
            Phrase  : """Введи название проекта.""",
            Next    : "update_draft_show_project",
            Input   : {Data:'name'},
        },
        "update_project_set_description" : {
            Type    : Get,
            Phrase  : """Введи описание проекта.""",
            Next    : "update_draft_show_project",
            Input   : {Data:'description'},
        },
        "update_issue_get_id" : {
            Type    : Get,
            Info    : "no_help",
            Phrase  : """Инициализирую переменные... Введи ID задачи.""",
            Next    : "update_issue_menu",
            Set     :   {
                            Storage  : { Context : Issue }
                        },
            Input   : {Parameters: "id"},
            Functions   :   [
                                "get_data",
                                ["reset_to_start","""not user.variables[Storage][Success]"""],
                                "show_storage_data", # Show user.variables[Storage][Data]
                            ],
        },
        "update_draft_show_issue" : {
            Type    : Say,
            Phrase  : """Черновик задачи""",
            Next    : "update_issue_menu",
            Functions: ["show_issue_update_draft"],
            Properties : [Lexeme_preserving]
        },
        "update_issue_menu" : {
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """Что ты хочешь поменять в задаче?""",
            Next    : {
                            "update_issue_set_project_id" : ["проект"],
                            "update_issue_set_subject" : ["тему","тема"],
                            "update_issue_set_parent_id" : ["родителя","родитель"],
                            "update_issue_set_description" : ["описание"],
                            "update_issue_set_notes" : ["примечание", "примечания"],
                            "update_issue_set_date" : ["дату","дата", "срок"],
                            "update_issue_set_assign0" : ["исполнителя","исполнитель", "назначена"],
                            "update_issue_set_tracker0" : ["трекер"],
                            "update_issue_set_status0" : ["статус"],
                            "update_issue_set_priority0" : ["приоритет"],
                            "update_call" : ["готово", "."]
                        },
        },
        "update_issue_set_assign0" : {
            Type    : Say,
            Next    : "update_issue_set_assign",
            Functions:["show_project_memberships"],
            Properties: [Lexeme_preserving]
        },
        "update_issue_set_tracker0" : {
            Type    : Say,
            Next    : "update_issue_set_tracker",
            Functions:["show_issue_trackers"],
            Properties: [Lexeme_preserving]
        },
        "update_issue_set_status0" : {
            Type    : Say,
            Next    : "update_issue_set_status",
            Functions:["show_issue_statuses"],
            Properties: [Lexeme_preserving]
        },
        "update_issue_set_priority0" : {
            Type    : Say,
            Next    : "update_issue_set_priority",
            Functions:["show_issue_priorities"],
            Properties: [Lexeme_preserving]
        },
        "update_issue_set_date":{
            Type    : Ask,
            Info    : "Здесь должна быть справка",
            Phrase  : """В чём?""",
            Next    :   {
                            "update_issue_set_date_start": ["начала"],
                            "update_issue_set_date_due" : ["завершения"]
                        },
        },
        "update_issue_set_project_id" : {
            Type    : Get,
            Phrase  : """Введи идентификатор проекта.""",
            Next    : "update_draft_show_issue",
            Input   : {Data:'project_id'},
        },
        "update_issue_set_parent_id" : {
            Type    : Get,
            Phrase  : """Введи идентификатор родительской задачи.""",
            Next    : "update_draft_show_issue",
            Input   : {Data:'parent_issue_id'},
        },
        "update_issue_set_subject" : {
            Type    : Get,
            Phrase  : """Введи тему.""",
            Next    : "update_draft_show_issue",
            Input   : {Data:'subject'},
        },
        "update_issue_set_description" : {
            Type    : Get,
            Phrase  : """Введи описание.""",
            Next    : "update_draft_show_issue",
            Input   : {Data:'description'},
        },
        "update_issue_set_notes" : {
            Type    : Get,
            Phrase  : """Введи примечания.""",
            Next    : "update_draft_show_issue",
            Input   : {Data:'notes'},
        },
        "update_issue_set_date_start" : {
            Type    : Get,
            Phrase  : """Введи дату начала. Например, 2023-08-02""",
            Next    : "update_draft_show_issue",
            Input   : {Data:'start_date'},
        },
        "update_issue_set_date_due" : {
            Type    : Get,
            Phrase  : """Введи срок завершения. Например, 2023-08-02""",
            Next    : "update_draft_show_issue",
            Input   : {Data:'due_date'},
        },
        "update_issue_set_assign" : {
            Type    : Get,
            Phrase  : """Введи id пользователя, которому хочешь назначить задачу.""",
            Next    : "update_draft_show_issue",
            Input   : {Data:'assigned_to_id'},
        },
        "update_issue_set_tracker" : {
            Type    : Get,
            Phrase  : """Введи ID трекера.""",
            Next    : "update_draft_show_issue",
            Input   : {Data:'tracker_id'},
        },
        "update_issue_set_status" : {
            Type    : Get,
            Phrase  : """Введи ID статуса.""",
            Next    : "update_draft_show_issue",
            Input   : {Data:'status_id'},
        },
        "update_issue_set_priority" : {
            Type    : Get,
            Phrase  : """Введи ID приоритета.""",
            Next    : "update_draft_show_issue",
            Input   : {Data:'priority_id'},
        },
        "update_call" : {
            Type     : Say,
            Error    : "Внести изменения не удалось.",
            Phrase   : """Изменения внесены успешно""",
            Next     : "reset_user",
            Functions: ["update"],
            Properties : [Lexeme_preserving]
        },
        "show" : {
            Type    : Ask,
            Phrase  : """Что ты хочешь посмотреть?""",
            Next    : {
                        "show_list":["список"],
                        "show_project_get_id":["проект"],
                        "show_issue_get_id":["задачу"],
                        "show_list_of_projects":["проекты"],
                        "show_list_of_issues":["задачи"],
                        "show_set_me_param":["мои"],
                        }
        },
        "show_set_me_param" : {
            Type    : Ask,
            Phrase  : """Список чего ты хочешь увидеть?""",
            Next    : {
                        "show_list_of_projects":["проекты"],
                        "show_list_of_issues":["задачи"]
            },
            Set     : { Parameters : { "assigned_to_id" : "me" } }
        },
        "show_list" : {
            Type    : Ask,
            Phrase  : """Список чего ты хочешь увидеть?""",
            Next    : {
                        "show_list_of_projects":["проектов"],
                        "show_list_of_issues":["задач"]
            }
        },
        "show_list_of_projects" : {
            Type    : Say,
            Error   : "Мне не удалось получить список проектов",
            Next    : "reset_user",
            Functions: ["get_project_list"],
            Properties : [Lexeme_preserving]
        },
        "show_list_of_issues" : {
            Type     : Say,
            Error    : "Мне не удалось получить список задач",
            Next     : "reset_user",
            Functions: ["get_issue_list"],
            Properties : [Lexeme_preserving]
        },
        "show_project_get_id" : {
            Type    : Get,
            Info    : "no_help",
            Phrase  : """Какой проект ты хочешь посмотреть?""",
            Next    : "show_call",
            Input   : {Parameters:'id'},
            Set     :   {
                            Storage     : { Context : Project },
                            Parameters  : {"include": "trackers"},
                        },
        },
        "show_issue_get_id" : {
            Type    : Get,
            Info    : "no_help",
            Phrase  : """Какую задачу ты хочешь посмотреть?""",
            Next    : "show_call",
            Input   : {Parameters:'id'},
            Set     : { Storage  : { Context : Issue } }
        },
        "show_call" : {
            Type     : Say,
            Error    : "data_get_error",
            Info     : "no_help",
            Phrase   : """Я получила следующую информацию.""",
            Next     : "reset_user",
            Functions: ["show"],
            Properties : [Lexeme_preserving]
        },
        "settings" : {
            Type    : Ask,
            Info    : "settings",
            Phrase  : "Что ты хочешь настроить? ('ничего' или '.' - выход из режима настройки)",
            Next    :   {
                        "set_key" : ["ключ"],
                        "start" : ["ничего", "."]
                        }
        },
        "set_key" : {
            Type    : Get,
            Info    : "settings",
            Phrase  : "Введи свой ключ API.",
            Input   : {Settings : Key},
            Next    : "set_key_feedback"
        },
        "set_key_feedback" : {
            Type    : Say,
            Info    : "settings",
            Phrase  : "Я запомнила твой ключ ({Settings[Key]}). Перехожу в режим настройки.",
            Next    : "settings",
            Properties: [Phrase_formatting, Lexeme_preserving, Say_anyway]
        },


    },
    Phrases : {
        Default : "...",
        Notification : "Список ",
        "set_approve_mode_phrase":"""Подтверждать изменения? (да/нет, сейчас установлено '{Settings[Approve_changes]}')""",
        "setted_approve_mode":"Установила подтверждение изменений: '{Settings[Approve_changes]}'",
    },
    Errors  : {
        Default : "Запрос некорректен, проверь его.",
        Notification : "Возникла непредвиденная ошибка в уведомлении.",
        "data_get_error" : "Мне не удалось получить данные.",
    },
    Infos   : {
        "no_help" : """По данному разделу справочная информация отсутствует.""",
        Default : """Команды строятся из глагола в повелительном наклонении и объекта над которым необходимо произвести действие.
В ответ на незавершенную команду я выдам наводящую фразу.

Замечу, что все лексемы я разбираю аналогично командной строке, т.е. если записать в кавычках "В чащах юга жил-был цитрус...", то я интерпретирую это не как отдельные слова, а как целую строку.

Если тебе нужна будет справка, то в любой момент ты можешь получить её с помощью слов "!справка" и "!помощь".
Для возврата в начальное состояние - "!отмена". Чтобы сбросить не только состояние, но и настройки, отправь "!сброс".

P.S.
@Fe_Ti просил передать, что я пока не разучилась падать. Поэтому при неполадках со мной обращаться к нему.
""",
        "select"    : """Задание контекста нужно для того, чтобы я понимала в каком объекте я работаю.""",
        "settings"  : """Здесь ты можешь настроить ключ API.
И другие переменные, когда они появятся."""
    },
    Commands : {
        Info      : ["!справка", "!помощь"],
        Reset     : ["!сброс"],
        Cancel    : ["!отмена"],
        Repeat    : ["!повтори"]
    },
}
