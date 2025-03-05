# UQUIX Responses Analyzing Configuration Guide

*This guide will help you to detected vulnerabilites based on your own AND/OR logics.

*If you want to customize your analyzing logic then use `--analyze-by`.

**`--analyze-by` will flag the specific keys in red for all requests for the same URL only if there's a difference in keys in one of the requests.

## Key Comparison Metrics

| Key               | Description                                  | Example Scenario                     |
|-------------------|----------------------------------------------|--------------------------------------|
| **STATUS**        | HTTPs status code differences                | `200` vs `403`                       |
| **CONTENT**       | Content length variations                    | `502b` vs `109b`                     |
| **METHOD**        | HTTPs method discrepancies                   | `GET` vs `POST`                      |
| **TITLE**         | Page title changes                           | "Login" vs "Admin Dashboard"         |
| **DURATION**      | Response time anomalies                      | `0.3004s` vs `0.2001s`               |
| **REQ_HDRS**      | Request header count changes                 | `5` vs `8`                           |
| **REQ_HDRS_SIZE** | Total size of request headers                | `1500b` vs `300b`                    |
| **RES_HDRS**      | Response header count changes                | `4` vs `7`                           |
| **RES_HDRS_SIZE** | Total size of response headers               | `200b` vs `450b`                     |
| **PAYLOADS_SIZE** | Request body size variations                 | `70b` vs `103b`                      |

## Logic Operators

- **AND**: ALL conditions must match and all that condition keys will be flagged in red. 
- **OR**: ANY condition can match and all that condition keys will be flagged in red.

## NOTES:
    
    **The order of keys and logic operators are important**
    **The analyzing table will be automatically sorted**
    **You can save analyzing results to a file using `--output-analyze`**

## Troubleshooting

|    **Issue**	             |    **Solution**                                                              |
|----------------------------|------------------------------------------------------------------------------|
|    False flags	         |    Use AND instead of OR                                                     |
|    Missed vulnerabilities	 |    Add more OR combinations                                                  |
|    Slow analysis	         |    Check the huge size of CONTENT/PAYLOADS_SIZE/REQ_HDRS_SIZE/RES_HDRS_SIZE  |

## Examples:

- **Header Analysis Focus**: `--analyze-by "(REQ_HDRS AND REQ_HDRS_SIZE) OR (RES_HDRS AND RES_HDRS_SIZE)"`
- **Advanced Anomaly Detection**: `--analyze-by "(STATUS AND METHOD) OR (TITLE AND CONTENT) OR (DURATION AND PAYLOADS_SIZE) OR (DURATION AND RES_HDRS_SIZE)"`
- **Strict Validation**: `--analyze-by "(REQ_HDRS_SIZE AND RES_HDRS_SIZE AND PAYLOADS_SIZE) OR (STATUS AND TITLE AND CONTENT)"`

## Default Configuration
```bash
--analyze-by "STATUS and CONTENT and METHOD and TITLE 
or STATUS and CONTENT and METHOD 
or STATUS and CONTENT and TITLE 
or STATUS and METHOD and TITLE 
or CONTENT and METHOD and TITLE 
or STATUS and CONTENT 
or STATUS and METHOD 
or STATUS and TITLE 
or CONTENT and METHOD 
or CONTENT and TITLE 
or METHOD and TITLE 
or STATUS 
or CONTENT 
or TITLE 
or METHOD 
or RES_HDRS and RES_HDRS_SIZE 
or RES_HDRS 
or RES_HDRS_SIZE 
or REQ_HDRS and REQ_HDRS_SIZE 
or REQ_HDRS 
or REQ_HDRS_SIZE 
or PAYLOAD_SIZE 
or DURATION"
```

################################################################
- By: Abd Almoen Arafa (0.1Arafa)
- WARNING: Please ask for PERMISSIONS before testing any web server
