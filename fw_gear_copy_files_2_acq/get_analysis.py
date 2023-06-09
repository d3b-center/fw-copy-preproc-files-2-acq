"""Handle pixelmed function."""
import logging

log = logging.getLogger(__name__)

def get_matching_analysis(session_container, gear_name: str):
    analyses = session_container.analyses
    if analyses:
        # print(f'     {session_container.label} has analysis containers')
        # Check to see if any were generated by our gear
        matches = [asys for asys in analyses if asys.gear_info.get('name') == gear_name]
        # Loop through the analyses and first make sure we only look at successful runs
        matches = [asys for asys in matches if asys.job.get('state')=='complete']
        log.info(f'     {len(matches)} completed matches found for gear - {gear_name} - (if >1, using the most recent one)')
        # if there are none, throw an error and exit
        if len(matches) == 0:
            log.error(f'    >>> ERROR: no analysis containers found in this session for the gear - {gear_name}')
        # if there's only 1, that's our match
        elif len(matches) == 1:
            match = matches[0]
        # If there are more than one matches (due to reruns), take the most recent run.
        else:
            # Now find the max run date (most recent), and extract the analysis that has that date.
            last_run_date = max([asys.created for asys in matches])
            last_run_analysis = [asys for asys in matches if asys.created == last_run_date]
            # There should only be one exact match.  If there are two successful runs that happened at the same time,
            # Something is strange...just take one at random.
            match = last_run_analysis[0]
        return match
    else:
        log.error('     >>> ERROR: no analysis containers found in this session!')
        return []
