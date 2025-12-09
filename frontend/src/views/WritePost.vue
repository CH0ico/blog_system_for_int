<template>
	<div class="write-page" v-loading="loading">
		<div class="container">
			<div class="page-header">
				<div>
					<h1>{{ isEdit ? '编辑文章' : '写文章' }}</h1>
					<p>支持 Markdown，保存草稿或直接发布</p>
				</div>
				<div class="header-actions">
					<el-button @click="saveDraft" :loading="saving">保存草稿</el-button>
					<el-button type="primary" @click="publishPost" :loading="saving">发布文章</el-button>
				</div>
			</div>

			<el-form ref="formRef" :model="form" :rules="rules" label-width="80px" class="write-form">
				<el-form-item label="标题" prop="title">
					<el-input v-model="form.title" placeholder="请输入文章标题" />
				</el-form-item>

				<el-form-item label="摘要" prop="summary">
					<el-input
						v-model="form.summary"
						type="textarea"
						:rows="3"
						placeholder="可选，不填将自动生成"
					/>
				</el-form-item>

				<el-form-item label="标签" prop="tags">
					<el-select
						v-model="form.tags"
						multiple
						filterable
						allow-create
						default-first-option
						placeholder="输入或选择标签"
					>
						<el-option
							v-for="tag in tagOptions"
							:key="tag.slug"
							:label="tag.name"
							:value="tag.name"
						/>
					</el-select>
				</el-form-item>

				<el-form-item label="分类" prop="categories">
					<el-select
						v-model="form.categories"
						multiple
						filterable
						allow-create
						default-first-option
						placeholder="选择分类"
					>
						<el-option
							v-for="cat in categoryOptions"
							:key="cat.slug"
							:label="cat.name"
							:value="cat.name"
						/>
					</el-select>
				</el-form-item>

				<el-form-item label="选项">
					<div class="options-row">
						<el-switch v-model="form.allow_comments" active-text="允许评论" />
						<el-switch v-model="form.is_featured" active-text="推荐" />
					</div>
				</el-form-item>

				<el-form-item label="内容" prop="content">
					<div class="editor">
						<el-input
							v-model="form.content"
							type="textarea"
							:rows="20"
							resize="vertical"
							placeholder="使用 Markdown 编写正文，支持代码高亮"
						/>
						<div class="preview" v-html="previewHtml"></div>
					</div>
				</el-form-item>

				<el-form-item>
					<el-space>
						<el-button @click="saveDraft" :loading="saving">保存草稿</el-button>
						<el-button type="primary" @click="publishPost" :loading="saving">发布文章</el-button>
					</el-space>
				</el-form-item>
			</el-form>
		</div>
	</div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import hljs from 'highlight.js'
import { usePostsStore } from '@/stores/posts'

const route = useRoute()
const router = useRouter()
const postsStore = usePostsStore()

const formRef = ref(null)
const loading = ref(false)
const saving = ref(false)
const tagOptions = ref([])
const categoryOptions = ref([])

const form = reactive({
	title: '',
	summary: '',
	tags: [],
	categories: [],
	content: '',
	status: 'draft',
	allow_comments: true,
	is_featured: false
})

const rules = {
	title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
	content: [{ required: true, message: '请输入正文', trigger: 'blur' }]
}

const isEdit = computed(() => Boolean(route.params.id || route.query.id))
const currentId = computed(() => route.params.id || route.query.id)

marked.setOptions({
	highlight(code, lang) {
		if (lang && hljs.getLanguage(lang)) {
			return hljs.highlight(code, { language: lang }).value
		}
		return hljs.highlightAuto(code).value
	}
})

const previewHtml = computed(() => marked.parse(form.content || ''))

const loadMeta = async () => {
	try {
		const [tagsRes, catsRes] = await Promise.all([
			fetch('/api/posts/tags'),
			fetch('/api/posts/categories')
		])
		tagOptions.value = (await tagsRes.json()).tags || []
		categoryOptions.value = (await catsRes.json()).categories || []
	} catch (error) {
		console.error('加载标签/分类失败', error)
	}
}

const loadPost = async () => {
	if (!isEdit.value) return
	loading.value = true
	try {
		const post = await postsStore.fetchPost(currentId.value)
		form.title = post.title
		form.summary = post.summary
		form.tags = post.tags?.map((t) => t.name) || []
		form.categories = post.categories?.map((c) => c.name) || []
		form.content = post.content
		form.allow_comments = post.allow_comments
		form.is_featured = post.is_featured
		form.status = post.status
	} catch (error) {
		ElMessage.error('加载文章失败')
	} finally {
		loading.value = false
	}
}

const submit = async (status = 'draft') => {
	const valid = await formRef.value.validate().catch(() => false)
	if (!valid) return
	saving.value = true
	try {
		form.status = status
		const payload = { ...form }
		const post = isEdit.value
			? await postsStore.updatePost(currentId.value, payload)
			: await postsStore.createPost(payload)
		ElMessage.success(status === 'published' ? '发布成功' : '草稿已保存')
		router.push(`/post/${post.id}`)
	} catch (error) {
		// 错误提示由 store 负责
	} finally {
		saving.value = false
	}
}

const saveDraft = () => submit('draft')
const publishPost = () => submit('published')

onMounted(() => {
	loadMeta()
	loadPost()
})
</script>

<style scoped>
.write-page {
	padding: 24px 0;
	background: var(--el-bg-color-page);
	min-height: 100vh;
}
.container {
	max-width: 1100px;
	margin: 0 auto;
	padding: 0 20px;
}
.page-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 16px;
}
.page-header h1 {
	margin: 0;
}
.header-actions {
	display: flex;
	gap: 8px;
}
.write-form {
	background: #fff;
	padding: 16px;
	border-radius: 8px;
	border: 1px solid var(--el-border-color-lighter);
}
.options-row {
	display: flex;
	gap: 16px;
}
.editor {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 16px;
}
.preview {
	border: 1px solid var(--el-border-color-lighter);
	border-radius: 8px;
	padding: 12px;
	min-height: 240px;
	background: var(--el-fill-color-lighter);
	overflow: auto;
}
.preview :deep(pre) {
	background: #1e1e1e;
	color: #fff;
	padding: 12px;
	border-radius: 6px;
	overflow: auto;
}
.preview :deep(code) {
	font-family: SFMono-Regular, Consolas, Menlo, Monaco, monospace;
}
@media (max-width: 900px) {
	.editor {
		grid-template-columns: 1fr;
	}
}
</style>
