from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def get_pagination(queryset, page_number=1, page_size=10):
    """
    This function applies pagination to a queryset.
    
    :param queryset: The queryset to paginate
    :param page_number: The page number to retrieve (defaults to 1)
    :param page_size: The number of items per page (defaults to 10)
    
    :return: A tuple containing:
        - A paginated queryset (page.object_list)
        - A dictionary with pagination metadata
    """
    paginator = Paginator(queryset, page_size)

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer, deliver the first page.
        page = paginator.page(1)
    except EmptyPage:
        # If the page number is out of range, deliver the last page of results.
        page = paginator.page(paginator.num_pages)

    response_data = {
        'current_page': page.number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
        'page_size': page_size,
    }

    return page.object_list, response_data