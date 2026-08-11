const FLASK_TASK_BASE_URL = 'http://127.0.0.1:8000/task'

export async function GET(
  request: Request,
  { params }: { params: Promise<{ task_id: string }> },
) {
  const { task_id } = await params
  const headers = new Headers()
  const cookie = request.headers.get('cookie')

  if (cookie) headers.set('cookie', cookie)

  const response = await fetch(
    `${FLASK_TASK_BASE_URL}/${encodeURIComponent(task_id)}`,
    {
      method: 'GET',
      headers,
      cache: 'no-store',
    },
  )

  const responseHeaders = new Headers()
  for (const name of ['cache-control', 'content-type', 'location']) {
    const value = response.headers.get(name)
    if (value) responseHeaders.set(name, value)
  }

  for (const setCookie of response.headers.getSetCookie()) {
    responseHeaders.append('set-cookie', setCookie)
  }

  return new Response(response.body, {
    status: response.status,
    headers: responseHeaders,
  })
}
