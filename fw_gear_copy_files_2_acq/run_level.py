
#!/usr/bin/env python3
"""Determine level at which the gear is running."""

import logging

# from flywheel import ApiException

log = logging.getLogger(__name__)


def get_analysis_run_level_and_hierarchy(fw_core_client, destination_id):
    """Determine the level at which a job is running, given a destination
    Args:
        fw (gear_toolkit.GearToolkitContext.client): flywheel client
        destination_id (id): id of the destination of the gear
    Returns:
        hierarchy (dict): containing the run_level and labels for the
            run_label, group, project, subject, session, and
            acquisition.
    """

    hierarchy = {
        "run_level": "no_destination",
        "run_label": "unknown",
        "group": None,
        "project_label": None,
        "subject_label": None,
        "session_label": None,
    }

    destination = fw_core_client.get(destination_id)
    if destination.container_type == "session":
        log.error("The destination_id must reference a valid session container.")

        hierarchy["run_level"] = destination.parent.type
        hierarchy["group"] = destination.parents["group"]

        for level in ["project", "subject", "session"]:
            if destination.parents[level]:
                container = fw_core_client.get(destination.parents[level])
                hierarchy[f"{level}_label"] = container.label
                if hierarchy["run_level"] == level:
                    hierarchy["run_label"] = container.label

    log.info(f"Gear run level and hierarchy labels: {hierarchy}")
    return hierarchy
