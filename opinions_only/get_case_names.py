# 1: liberal
# 2: conservative
# 3: unspecifiable

import requests

def make_api_request(url: str, headers: dict, params={}) -> dict:
    print("Trying URL: ", url)
    response = requests.get(url, headers=headers, params=params, timeout=(10,60))
    response.raise_for_status()
    return response.json()

api_key = "80e9ea74585c372bc72c0c9247852286d4a521fb"

headers = {
    # Authorization header with the API key
    "Authorization": f"Token {api_key}"
}


base_opinion_url = "https://www.courtlistener.com/api/rest/v4/opinions/"
base_cluster_url = "https://www.courtlistener.com/api/rest/v4/clusters/"


scdb_decision_direction_dict = {
    1: "liberal",
    2: "conservative",
    3: "unspecified"
}

def fetch_cluster_data(case_ids, base_opinion_url, base_cluster_url, headers):
    """
    Fetches cluster data for a list of case IDs.

    Parameters:
        case_ids (list): List of case IDs to fetch data for.
        base_opinion_url (str): Base URL for the opinions API.
        base_cluster_url (str): Base URL for the clusters API.
        headers (dict): Headers for the API requests.

    Returns:
        list: List of dictionaries containing cluster data.
    """
    results = {}

    for case_id in case_ids:
        # Fetch the cluster ID from the opinions API
        opinion_params = {
            "id": f"{case_id}",
            "fields": "cluster_id,type",
        }
        cluster_url_response = make_api_request(base_opinion_url, headers, opinion_params)

        if not cluster_url_response["results"]:
            print(f"No cluster found for case ID: {case_id}")
            continue

        cluster_id = cluster_url_response["results"][0]["cluster_id"]

        # Fetch cluster data using the cluster ID
        cluster_params = {
            "id": cluster_id,
            "fields": "case_name,case_name_full,scdb_decision_direction,scdb_votes_majority,scdb_votes_minority,summary",
        }
        cluster_data_response = make_api_request(base_cluster_url, headers, cluster_params)

        if not cluster_data_response["results"]:
            print(f"No data found for cluster ID: {cluster_id}")
            continue

        cluster_data = cluster_data_response["results"][0]
        # Map decision direction
        cluster_data["scdb_decision_direction"] = scdb_decision_direction_dict.get(
            cluster_data["scdb_decision_direction"], "unknown"
        )

        if "type" in cluster_url_response["results"][0]:
            cluster_data["type"] = cluster_url_response["results"][0]["type"]

        results[case_id] = cluster_data

    return results

# Example usage
case_ids = [93982, 93982, 93982]  # Replace with your list of case IDs
test = fetch_cluster_data(case_ids, base_opinion_url, base_cluster_url, headers)
print(test)


# cluster_data_response = make_api_request(base_cluster_url, headers, cluster_params)["results"][0]
# scdb_decision_direction_dict = {
#     1: "liberal",
#     2: "conservative",
#     3: "unspecified"
# }
# cluster_data_response["scdb_decision_direction"] = scdb_decision_direction_dict[cluster_data_response["scdb_decision_direction"]]

# print(cluster_data_response)


# def get_cluster_data_for_cases(case_ids: list) -> list:
#     cluster_data_responses = []
#     opinion_params = {
#         "id__in": ",".join(map(str, case_ids)),  # Join case_ids into a comma-separated string
#         "fields": "cluster_id",
#     }
    
#     # Make a single API request for all case_ids
#     cluster_url_response = make_api_request(base_opinion_url, headers, opinion_params)
    
#     for result in cluster_url_response["results"]:
#         cluster_id = result["cluster_id"]

#         cluster_params = {
#             "id": cluster_id,
#             "fields": "case_name,case_name_full,scdb_decision_direction,scdb_votes_majority,scdb_votes_minority,summary"
#         }

#         cluster_data_response = make_api_request(base_cluster_url, headers, cluster_params)["results"][0]
#         scdb_decision_direction_dict = {
#             1: "liberal",
#             2: "conservative",
#             3: "unspecified"
#         }
#         print("initial cluster_data_response: ", cluster_data_response)
#         cluster_data_response["scdb_decision_direction"] = scdb_decision_direction_dict[cluster_data_response["scdb_decision_direction"]]
        
#         cluster_data_responses.append(cluster_data_response)

#     return cluster_data_responses



# all_cluster_data = get_cluster_data_for_cases(case_ids)
# print(all_cluster_data)



# import requests

# url = "https://www.courtlistener.com/api/rest/v4/clusters"  # Replace with your API endpoint
# # params = {"scdb_decision_direction": "1"}  # Example parameter
# params = {}
# response = requests.get(url, params=params)
# # response = requests.options(url)

# if response.status_code == 200:
#     test_response = response.json()
#     if "scdb_decision_direction" in test_response:
#         print(test_response["scdb_decision_direction"])
#     # print(response.json())  # The response usually contains field descriptions and options
# else:
#     print(f"Failed to fetch OPTIONS. Status code: {response.status_code}")


# import requests

# # URL for the CourtListener API
# url = "https://www.courtlistener.com/api/rest/v4/clusters"

# # Send an OPTIONS request
# response = requests.options(url)

# # Print the response headers and status code
# print(f"Status Code: {response.status_code}")
# print("Headers:")
# for key, value in response.headers.items():
#     print(f"{key}: {value}")


