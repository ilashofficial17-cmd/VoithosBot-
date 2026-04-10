"""Простая аналитика через логгер — попадает в Railway logs."""
import logging

logger = logging.getLogger("analytics")


def track_button(user, button: str) -> None:
    """Трекинг нажатий кнопок."""
    logger.info(
        f"[ANALYTICS] button={button} | "
        f"user_id={user.id} | name={user.first_name} | "
        f"username=@{user.username or '-'}"
    )


def track_demo_start(user) -> None:
    logger.info(
        f"[ANALYTICS] event=demo_start | "
        f"user_id={user.id} | name={user.first_name} | "
        f"username=@{user.username or '-'}"
    )


def track_demo_end(user, messages: int, reason: str) -> None:
    logger.info(
        f"[ANALYTICS] event=demo_end | reason={reason} | messages={messages} | "
        f"user_id={user.id} | name={user.first_name} | "
        f"username=@{user.username or '-'}"
    )


def log_demo_summary(user, summary: str, messages: int) -> None:
    """Сводка диалога демки от AI."""
    logger.info(
        f"[DEMO_SUMMARY] user=@{user.username or user.first_name} "
        f"({user.id}) | msgs={messages}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n{summary}\n━━━━━━━━━━━━━━━━━━━━━"
    )
