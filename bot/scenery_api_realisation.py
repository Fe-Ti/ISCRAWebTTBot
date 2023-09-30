# Copyright 2023 Fe-Ti aka T.Kravchenko

import json
import logging
from datetime import date

from redminebotlib import *
from redminebotlib.default_scenery_api_realisation import get_string_from_enum_list

class ApiRealisationTemplates(DefaultApiRealisationTemplates):
    issue = """№{id} {subject}

Описание: {description}

Автор: {author[name]} ({author[id]})
Трекер: {tracker[name]} ({tracker[id]})

Дата начала: {start_date}
Срок завершения: {due_date}
Приоритет: {priority[name]}({priority[id]})
Статус: {status[name]}({status[id]})
"""
    issue_assigned_to = "Назначена: {assigned_to[name]} ({assigned_to[id]})"
    issue_parent_issue = "Родительская задача: {parent[id]}"


    issue_draft = """Черновик задачи:
Тема: {subject}
ID проекта: {project_id}
Родительская задача: {parent_issue_id}
Описание: {description}

Дата начала: {start_date}
Срок завершения: {due_date}
Статус: {status_id}

Назначена: {assigned_to_id}
Трекер: {tracker_id}
Приоритет: {priority_id}"""

    issue_update_draft = """Изменения в задаче:{}"""
    issue_update_dict = {
        "notes"         : "\nПримечания:",
        "project_id"    : "\nID проекта:",
        "project_id"    : "\nID задачи-родителя:",
        "subject"       : "\nТема:",
        "description"   : "\nОписание:",
        "start_date"    : "\nДата начала:",
        "due_date"      : "\nСрок завершения:",
        "status_id"        : "\nСтатус:",
        "assigned_to_id"   : "\nНазначена:",
        "tracker_id"       : "\nТрекер:",
        "priority_id"       : "\nТрекер:",
    }


    project = """{name} ({identifier})

Описание:   {description}

Участники:
"""
    project_draft = """Черновик проекта:
Название: {name}
Идентификатор: {identifier}
Описание: {description}
"""
    project_update_draft = project_draft

    project_custom_field = """{name}: {value}\n"""
    project_member_field = """{user[name]} (id:{user[id]}): {role_names}\n"""

    issue_custom_field = project_custom_field

    project_list_entry = """\n№{id} "{name}" ({identifier})"""

    issue_list_entry = """\n№{id} "{subject}" """

    issue_statuses = """Статусы: {}"""
    issue_statuses_list_entry = """\n{id} "{name}" """
    issue_trackers = """Трекеры: {}"""
    issue_trackers_list_entry = issue_statuses_list_entry
    issue_priorities = """Приоритеты: {}"""
    issue_priorities_list_entry = issue_statuses_list_entry

    notification_header = "Я проверила список твоих задач."
    notification_no_issues = " Он оказался пуст. :("
    notification_issues_found = " Они такие:\n{}"
    days_before_due_date = "(срок {}д.)"
    expired_due_date = "(опоздание {}д.)"
    server_error = "Набор ошибок от сервера: {}."

class SceneryApiRealisation(DefaultSceneryApiRealisation):
    ### Functions which don't use redmine API
    def reset_user(self, user):
        # ~ print(user)
        self.bot.reset_user(user, keep_settings=True, reset_state=False)
        # ~ print(user.state)

    def push_state_to_stack(self, user):
        storage = user.variables[Storage]
        if State_stack not in storage:
            storage[State_stack] = list()
        if JMP_state in storage:
            storage[State_stack].append(user.state.name)
            user.state = self.bot.scenery_states[storage[JMP_state]]

    def pop_state_from_tack(self, user):
        storage = user.variables[Storage]
        if State_stack not in storage:
            logging.warning("No stack initialized. (User:{user.uid})")
            return
        if not storage[State_stack]:
            logging.warning(f"Stack is empty. (User:{user.uid})")
            return
        state_name = storage[State_stack].pop()
        user.state = self.bot.scenery_states[state_name]

    def call_state(self, user):
        push_state_to_stack()
        self.bot._run_state(user)
        pop_state_from_stack()

    def reset_to_start(self, user):
        self.bot.reset_user(user, keep_settings=True, reset_state=True)

    def report_failure(self, user, resp_data=list()):
        self.bot.reply_function(Message(user.uid, user.state.error))
        if "errors" in resp_data["data"]:
            resp_data["data"] = json.loads(resp_data["data"])
            self.bot.reply_function(
                Message(user.uid,
                    self.templates.server_error.format(resp_data["data"]["errors"]))
                )
    ### Functions which call ServerControlUnit functions (i.e. use RM API)

    def _notify(self, user):
        resp_data = self.bot.scu.get_issue_list({ "assigned_to_id" : "me" },
                                user.variables[Settings][Key])
        string = str()
        if resp_data[Success]:
            today = date.today()
            for issue in resp_data["data"]["issues"]:
                string += self.templates.issue_list_entry.format_map(issue)
                if "due_date" in issue:
                    due_date = date.fromisoformat(issue["due_date"])
                    days_delta = (due_date - today).days
                    if days_delta < 0:
                        days_delta = abs(days_delta)
                        template = self.templates.expired_due_date
                    else:
                        template = self.templates.days_before_due_date
                    string += template.format(days_delta)
            if string:
                string = self.templates.notification_header + self.templates.notification_issues_found.format(string)
                self.bot.reply_function(Message(user.uid, string))
            else:
                string = self.templates.notification_header + self.templates.notification_no_issues
                self.bot.reply_function(Message(user.uid, string))

    def create(self, user):
        self._clear_nulls(user.variables[Data])
        if user.variables[Storage][Context] == Project:
            resp_data = self.bot.scu.create_project(user.variables[Parameters],
                                    user.variables[Data],
                                    user.variables[Settings][Key])
        elif user.variables[Storage][Context] == Issue:
            resp_data = self.bot.scu.create_issue(user.variables[Parameters],
                                    user.variables[Data],
                                    user.variables[Settings][Key])
        else:
            logging.error("Context is not set correctly. Please check your scenery.")
            return
        if resp_data[Success]:
            issue = resp_data["data"]["issue"]
            string = self.templates.issue.format_map(issue)
            if "assigned_to" in issue:
                string += self.templates.issue_assigned_to.format_map(issue)
            if "custom_fields" in issue:
                for custom_field in issue["custom_fields"]:
                    string += self.templates.project_custom_field.format_map(custom_field)
            self.bot.reply_function(Message(user.uid, user.state.phrase))
            self.bot.reply_function(Message(user.uid, string))
        else:
            self.report_failure(user, resp_data)

    def _project_to_str(self, user, project):
        string = self.templates.project.format_map(project)
        if "custom_fields" in project:
            for custom_field in project["custom_fields"]:
                string += self.templates.project_custom_field.format_map(custom_field)
        string += self._get_project_memberships(user, project["id"])
        return string

    def _issue_to_str(self, user, issue):
        string = self.templates.issue.format_map(issue)
        if "assigned_to" in issue:
            string += self.templates.issue_assigned_to.format_map(issue)
        if "parent" in issue:
            string += self.templates.issue_parent_issue.format_map(issue)
        if "custom_fields" in issue:
            for custom_field in issue["custom_fields"]:
                string += self.templates.project_custom_field.format_map(custom_field)
        return string

    def show(self, user):
        if user.variables[Storage][Context] == Project:
            resp_data = self.bot.scu.show_project(user.variables[Parameters],
                                    user.variables[Settings][Key])
            if resp_data[Success]:
                project = resp_data["data"]["project"]
                string = self._project_to_str(user, project)
        elif user.variables[Storage][Context] == Issue:
            resp_data = self.bot.scu.show_issue(user.variables[Parameters],
                                    user.variables[Settings][Key])
            if resp_data[Success]:
                issue = resp_data["data"]["issue"]
                string = self._issue_to_str(user, issue)
        else:
            logging.error("Context is not set correctly. Please check your scenery.")
            return
        user.variables[Storage][Success] = resp_data[Success]
        if resp_data[Success]:
            self.bot.reply_function(Message(user.uid, string))
        else:
            self.report_failure(user, resp_data)

    def _process_empty_resp_data(self, user, resp_data):
        if resp_data[Success]:
            self.bot.reply_function(Message(user.uid, user.state.phrase))
        else:
            self.report_failure(user, resp_data)

    def update(self, user):
        # ~ print(user.variables[Data])
        self._clear_nulls(user.variables[Data])
        if user.variables[Storage][Context] == Project:
            resp_data = self.bot.scu.update_project(user.variables[Parameters],
                                    user.variables[Data],
                                    user.variables[Settings][Key])
        elif user.variables[Storage][Context] == Issue:

            resp_data = self.bot.scu.update_issue(user.variables[Parameters],
                                    user.variables[Data],
                                    user.variables[Settings][Key])
        else:
            logging.error("Context is not set correctly. Please check your scenery.")
            return
        # ~ print(resp_data)
        self._process_empty_resp_data(user, resp_data)

    def delete(self, user):
        if user.variables[Storage][Context] == Project:
            resp_data = self.bot.scu.delete_project(user.variables[Parameters]["id"],
                                    user.variables[Settings][Key])
        elif user.variables[Storage][Context] == Issue:
            resp_data = self.bot.scu.delete_issue(user.variables[Parameters]["id"],
                                    user.variables[Settings][Key])
        else:
            logging.error("Context is not set correctly. Please check your scenery.")
            return
        self._process_empty_resp_data(user, resp_data)

    def get_project_list(self, user):
        parameters = user.variables[Parameters]
        key = user.variables[Settings][Key]
        resp_data = self.bot.scu.get_project_list(parameters, key)
        user.variables[Storage][Success] = resp_data[Success]
        if resp_data[Success]:
            msg_string = str()
            for project in resp_data["data"]["projects"]:
                msg_string += self.templates.project_list_entry.format_map(project)

            if not msg_string:
                self.bot.reply_function(Message(user.uid, "Проектов нет."))
            else:
                self.bot.reply_function(Message(user.uid, msg_string))
        else:
            self._report_failure(user, resp_data)

    def get_issue_list(self, user):
        parameters = user.variables[Parameters]
        key = user.variables[Settings][Key]
        resp_data = self.bot.scu.get_issue_list(parameters, key)
        user.variables[Storage][Success] = resp_data[Success]
        if resp_data[Success]:
            msg_string = str()
            for issue in resp_data["data"]["issues"]:
                msg_string += self.templates.issue_list_entry.format_map(issue)
            if not msg_string:
                self.bot.reply_function(Message(user.uid, "Задач нет."))
            else:
                self.bot.reply_function(Message(user.uid, msg_string))
        else:
            self._report_failure(user, resp_data)

    def show_project_draft(self, user):
        self.bot.reply_function(Message(
                                    user.uid,
                                    self.templates.project_draft.format_map(user.variables[Data])
                                    ))

    def show_issue_draft(self, user):
        self.bot.reply_function(Message(
                                    user.uid,
                                    self.templates.issue_draft.format_map(user.variables[Data])
                                    ))

    def show_project_update_draft(self, user):
        self.bot.reply_function(Message(
                                    user.uid,
                                    self.templates.project_update_draft.format_map(user.variables[Storage][Data])
                                    ))
    def show_issue_update_draft(self, user):
        string = str()
        for key, translation in self.templates.issue_update_dict.items():
            if key in user.variables[Data]:
                string += f"{translation} {user.variables[Data][key]}"
        self.bot.reply_function(Message(
                                    user.uid,
                                    self.templates.issue_update_draft.format(string)
                                    ))

    def log_to_user(self, user, log_msg):
        self.bot.reply_function(Message(user.uid, log_msg))

    def _get_project_memberships(self, user, project_id):
        string = str()
        resp_data = self.bot.scu.get_project_memberships(project_id,
                                                    user.variables[Settings][Key])
        if resp_data[Success]:
            member = dict()
            for mship in resp_data["data"]["memberships"]:
                member["role_names"] = str({ role["name"] for role in mship["roles"] })[1:-1].replace("'","")
                member["user"] = mship["user"]
                string += self.templates.project_member_field.format_map(member)
        return string

    def show_project_memberships(self, user):
        if "identifier" in user.variables[Data]:
            project_id = user.variables[Data]["identifier"]
        elif "project_id" in user.variables[Data]:
            project_id = user.variables[Data]["project_id"]
        elif "project" in user.variables[Storage][Data]:
            project_id = user.variables[Storage][Data]["project"]["id"]
        else:
            raise KeyError("Can't show memberships, because project id is not scpecified.")
        string = self._get_project_memberships(user, project_id)
        if not string:
            return
        self.bot.reply_function(Message(user.uid, string))

    def _show_enumeration(self, user, enum_list, template, template_list_entry):
        if user.variables[Storage][Context] in [Project, Global, Issue]:
            self.bot.reply_function(Message(
                user.uid,
                template.format(get_string_from_enum_list(enum_list, template_list_entry))
                ))
        else:
            logging.error("Context is not set correctly. Please check your scenery.")
            return

    def show_issue_statuses(self, user):
        self._show_enumeration(
            user = user,
            enum_list = self.bot.issue_statuses,
            template = self.templates.issue_statuses,
            template_list_entry = self.templates.issue_statuses_list_entry,
        )

    def show_issue_trackers(self, user):
        self._show_enumeration(
            user = user,
            enum_list = self.bot.issue_trackers,
            template = self.templates.issue_trackers,
            template_list_entry = self.templates.issue_trackers_list_entry,
        )

    def show_issue_priorities(self, user):
        self._show_enumeration(
            user = user,
            enum_list = self.bot.issue_priorities,
            template = self.templates.issue_priorities,
            template_list_entry = self.templates.issue_priorities_list_entry,
        )

    # ~ def add_watcher(self, user):
        # ~ pass
    # ~ def delete_watcher(self, user):
        # ~ pass

    def get_data(self, user):
        context = user.variables[Storage][Context]
        if context == Project:
            resp_data = self.bot.scu.show_project(user.variables[Parameters],
                                                user.variables[Settings][Key])
        elif context == Issue:
            resp_data = self.bot.scu.show_issue(user.variables[Parameters],
                                                user.variables[Settings][Key])
        else:
            logging.error("Context is not set correctly. Please check your scenery.")
            return
        if resp_data[Success]:
            user.variables[Storage][Data] = resp_data["data"][context.lower()]
            user.variables[Storage][Success] = resp_data[Success]
        else:
            self._report_failure(user, resp_data)
            user.variables[Storage][Success] = False

    def show_storage_data(self, user):
        if user.variables[Storage][Context] == Project:
            string = self._project_to_str(user, user.variables[Storage][Data])
        elif user.variables[Storage][Context] == Issue:
            string = self._issue_to_str(user, user.variables[Storage][Data])
        else:
            logging.error("Context is not set correctly. Please check your scenery.")
            return
        self.bot.reply_function(Message(user.uid, string))

    def get_parent_issue_project_id(self, user):
        if "parent_issue_id" not in user.variables[Data]:
            return
        context = user.variables[Storage][Context]
        resp_data = self.bot.scu.show_issue({"id":user.variables[Data]["parent_issue_id"]},
                                            user.variables[Settings][Key])
        if resp_data[Success]:
            user.variables[Data]["project_id"] = resp_data["data"][context.lower()]["project"]["id"]
            user.variables[Storage][Success] = resp_data[Success]
        else:
            # ~ self._report_failure(user, resp_data)
            user.variables[Storage][Success] = False

