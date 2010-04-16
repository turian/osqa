from forum.models import Question

def question_search(keywords):
    return Question.objects.extra(
                    select={
                        'ranking': "node_ranking(id, %s)",
                    },
                    where=["node_ranking(id, %s) > 0"],
                    params=[keywords],
                    select_params=[keywords]
                ).order_by('-ranking')