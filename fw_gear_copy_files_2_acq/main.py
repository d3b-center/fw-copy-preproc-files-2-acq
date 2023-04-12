"""Main module."""
# import gzip
import logging
# import tempfile
# from contextlib import ExitStack
# from pathlib import Path
import os

from fw_core_client import CoreClient
from flywheel_gear_toolkit import GearToolkitContext
import flywheel

from .run_level import get_analysis_run_level_and_hierarchy
from .get_analysis import get_matching_analysis

log = logging.getLogger(__name__)

fw_context = flywheel.GearContext()
fw = fw_context.client

def run(client: CoreClient, gtk_context: GearToolkitContext):
    """Main entrypoint

    Args:
        client (CoreClient): Client to connect to API
        gtk_context (GearToolkitContext)
    """
    # get the Flywheel hierarchy for the run
    destination_id = gtk_context.destination["id"]
    hierarchy = get_analysis_run_level_and_hierarchy(gtk_context.client, destination_id)
    sub_label = hierarchy['subject_label']
    ses_label = hierarchy['session_label']
    project_label = hierarchy['project_label']
    group_name = hierarchy['group']

    # now look for the analysis gear to grab files from (within the same session)
    ses = fw.lookup(f'{group_name}/{project_label}/{sub_label}/{ses_label}')
    ses = ses.reload()
    gear_name = 'd3b-ped-proc-pipeline-batch'
    match = get_matching_analysis(ses, gear_name)
    # if we have a matching gear, rename & copy the files to the acquisition container
    if match:
        match = match.reload()
        for file in match.files:
            fname = file.name
            if fname[-7:] == '.nii.gz': # if it's a nifti file
                match.download_file(fname, fname)
                base_fname = fname.split('.nii.gz')[0] # get the file name without the extension
                # define the output file name
                if 'T1CE_to_SRI' == base_fname:
                    out_fname = f'{sub_label}_{ses_label}_T1CE_to_SRI.nii.gz'
                elif 'T1_to_SRI' == base_fname:
                    out_fname = f'{sub_label}_{ses_label}_T1_to_SRI.nii.gz'
                elif 'T2_to_SRI' == base_fname:
                    out_fname = f'{sub_label}_{ses_label}_T2_to_SRI.nii.gz'
                elif 'FL_to_SRI' == base_fname:
                    out_fname = f'{sub_label}_{ses_label}_FL_to_SRI.nii.gz'
                elif 'brainTumorSegmentation_SRI' == base_fname:
                    out_fname = f'{sub_label}_{ses_label}_pred_tumorSegmentation.nii.gz'
                elif 'brainMask_SRI' == base_fname:
                    out_fname = f'{sub_label}_{ses_label}_pred_brainMask.nii.gz'
                elif 'z_T1_to_SRI_ss' == base_fname:
                    out_fname = f'{sub_label}_{ses_label}_T1_SRI_norm_ss.nii.gz'
                elif 'z_T1CE_to_SRI_ss' == base_fname:
                    out_fname = f'{sub_label}_{ses_label}_T1CE_SRI_norm_ss.nii.gz'
                elif 'z_T2_to_SRI_ss' == base_fname:
                    out_fname = f'{sub_label}_{ses_label}_T2_SRI_norm_ss.nii.gz'
                elif 'z_FL_to_SRI_ss' == base_fname:
                    out_fname = f'{sub_label}_{ses_label}_FL_SRI_norm_ss.nii.gz'
                else:
                    out_fname == []
                # if we have the output file name, upload file to the acquisition
                if out_fname == []:
                    log.error(f'>>> ERROR: no mapping to rename the file name - {fname}')
                    os.remove(fname)
                else:
                    # make the output location if it doesn't already exist
                    acq_label = 'processed'
                    try:
                        acq = fw.lookup(f'{group_name}/{project_label}/{sub_label}/{ses_label}/{acq_label}')
                    except:
                        acq = ses.add_acquisition({'label':acq_label})
                    # rename the file locally
                    os.rename(fname, out_fname)
                    # upload the renamed file to the target acquisition
                    fw.upload_file_to_acquisition(acq.id, out_fname)
                    log.info(f"Saved output file {out_fname}")
    else:
        log.error(f'>>> ERROR: found analysis containers but no completed runs for the gear - {gear_name}')
