from flask import Blueprint, current_app

# For some reason,
# db has to be imported for database instance to get created if it doesn't exist.
from status_dwarf.models import session, Target, TargetStrategy, db  # noqa

commands = Blueprint("commands", __name__)


def sync_targets(no_confirm=False) -> None:
    if not no_confirm:
        prompt = (
            "The following action will modify the the database and can result in"
            " data loss. This is IRREVERSIBLE.\n"
            "Are you sure that you want to continue? [y/N] ")
        verification = input(prompt).strip().lower()
        if verification != "y" and verification != "yes":
            print("Operation cancelled.")
            return
    targets_list = current_app.config["TARGETS"]
    for index, target in enumerate(targets_list, start=1):
        if len(target) == 2:
            target = target + ("",)
        existing_target = session.query(Target).filter_by(id=index).first()
        if not existing_target:
            session.add(Target(id=index, name=target[0], address=target[1],
                               strategy=TargetStrategy.str_to_strategy(target[2])))
        elif (
            existing_target.name, existing_target.address,
            existing_target.strategy) != (
            target[0], target[1], TargetStrategy.str_to_strategy(target[2])):
            session.delete(existing_target)
            session.add(Target(id=index, name=target[0], address=target[1],
                               strategy=TargetStrategy.str_to_strategy(target[2])))
    for existing_target in (
        session.query(Target).filter(Target.id > len(targets_list)).all()
    ):
        session.delete(existing_target)
    session.commit()
    print("Synchronization done!")


@commands.cli.command("sync_targets")
def sync_targets_command():
    return sync_targets()
