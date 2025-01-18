

def validate_job_title( job_title ):
    if "python" not in job_title.lower():
        return False
    else:
        return True


def validate_company_title( job_company ):
    if "rgb" in job_company.lower():
        return False
    else:
        return True



