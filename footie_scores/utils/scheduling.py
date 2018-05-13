import grequests as gr


def batch_request(urls):
    requests = (gr.get(url) for url in urls)
    responses = gr.map(requests)
    return responses
